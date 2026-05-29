import os
import sys
import argparse
import json
from dotenv import load_dotenv

# --- IMPORTANT: load env vars BEFORE importing langfuse / openai ---
# Langfuse reads LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST
# from env at import-time. Loading .env first ensures they're available.
load_dotenv()

from langfuse import observe, Langfuse, propagate_attributes
from langfuse.openai import OpenAI

# Add src to python path just in case
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.image_parser import parse_contract_image
from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent
from src.models import ContractChangeOutput

# Langfuse singleton
langfuse = Langfuse()


@observe(name="contract-analysis")
def run_pipeline(original_path: str, amendment_path: str) -> ContractChangeOutput:
    """
    Orchestrates the entire contract analysis pipeline.
    
    1. Transcribes original contract from image.
    2. Transcribes amendment from image.
    3. Structural alignment map generation.
    4. Structured changes extraction.
    
    All steps are tracked in Langfuse under a single hierarchical trace
    using the @observe decorator (Langfuse Python SDK v4 best practices).
    """
    # Propagate user_id and metadata to the current trace and all children
    with propagate_attributes(
        user_id="legalmove-user-1",
        metadata={
            "original_document": os.path.basename(original_path),
            "amendment_document": os.path.basename(amendment_path),
        },
    ):
        # Set explicit trace input (only relevant data, not all function args)
        langfuse.update_current_span(
            input={
                "original_path": original_path,
                "amendment_path": amendment_path,
            }
        )

        # Initialize auto-instrumented OpenAI client
        openai_client = OpenAI()

        try:
            # Step 1: Parse Original Contract
            print(f"Step 1/4: Parsing original contract image: {original_path}...")
            original_text = parse_contract_image(
                image_path=original_path,
                contract_type="original",
                openai_client=openai_client,
            )
            print(f"Original contract successfully transcribed ({len(original_text)} chars).")

            print("--------------------------------")
            print("Original contract text:")
            print(original_text)
            print("--------------------------------")

            # Step 2: Parse Amendment Contract
            print(f"Step 2/4: Parsing amendment contract image: {amendment_path}...")
            amendment_text = parse_contract_image(
                image_path=amendment_path,
                contract_type="amendment",
                openai_client=openai_client,
            )
            print(f"Amendment contract successfully transcribed ({len(amendment_text)} chars).")

            # Step 3: Contextual Clause Alignment
            print("Step 3/4: Generating contextual clause alignment map...")
            context_agent = ContextualizationAgent(openai_client=openai_client)
            alignment_map = context_agent.align_contracts(
                original_text=original_text,
                amendment_text=amendment_text,
            )
            print("Contextual alignment map generated successfully.")

            # Step 4: Structured Data Extraction
            print("Step 4/4: Extracting structured changes...")
            extract_agent = ExtractionAgent(openai_client=openai_client)
            structured_changes = extract_agent.extract_changes(
                original_text=original_text,
                amendment_text=amendment_text,
                alignment_map=alignment_map,
            )
            print("Structured changes extracted successfully.")

            # Update trace output
            langfuse.update_current_span(
                output=structured_changes.model_dump()
            )

            return structured_changes

        except Exception as e:
            # Update trace with error details
            langfuse.update_current_span(
                level="ERROR",
                status_message=str(e),
            )
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="LegalMove Contract Analysis Pipeline - AI Agents with Langfuse Tracing"
    )
    parser.add_argument(
        "--original",
        required=True,
        help="Path to the original contract image (.png, .jpg, .jpeg)",
    )
    parser.add_argument(
        "--amendment",
        required=True,
        help="Path to the amendment image (.png, .jpg, .jpeg)",
    )

    args = parser.parse_args()

    # Validate environment
    if not os.environ.get("OPENAI_API_KEY"):
        print("[ERROR] Missing OPENAI_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)
    if not os.environ.get("LANGFUSE_PUBLIC_KEY") or not os.environ.get("LANGFUSE_SECRET_KEY"):
        print("[WARNING] Langfuse keys not found. Tracing may be disabled.")

    try:
        results = run_pipeline(args.original, args.amendment)
        print("\n=== PIPELINE COMPLETED SUCCESSFULLY ===")
        print(json.dumps(results.model_dump(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\n[ERROR] Pipeline execution failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Ensure all events are sent to Langfuse before exiting
        print("Flushing Langfuse events...")
        langfuse.flush()
