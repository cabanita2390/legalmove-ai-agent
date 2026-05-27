import os
import sys
import json
from unittest.mock import MagicMock, patch

# Ensure src is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set mock environment variables BEFORE importing langfuse/openai modules
os.environ["OPENAI_API_KEY"] = "mock-openai-key"
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-mock"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-mock"
os.environ["LANGFUSE_HOST"] = "https://mock.langfuse.com"

from src.models import ContractChangeOutput


def create_dummy_images():
    """Creates two dummy files representing contract images."""
    print("Creating dummy files for mock testing...")
    with open("dummy_original.png", "wb") as f:
        f.write(b"fake png original contract bytes")
    with open("dummy_amendment.png", "wb") as f:
        f.write(b"fake png amendment contract bytes")


def cleanup_dummy_images():
    """Removes dummy files."""
    print("Cleaning up dummy files...")
    if os.path.exists("dummy_original.png"):
        os.remove("dummy_original.png")
    if os.path.exists("dummy_amendment.png"):
        os.remove("dummy_amendment.png")


@patch("src.image_parser.Langfuse")
@patch("src.agents.contextualization_agent.Langfuse")
@patch("src.agents.extraction_agent.Langfuse")
@patch("src.main.Langfuse")
@patch("src.main.OpenAI")
@patch("src.main.propagate_attributes")
def test_pipeline_flow(
    mock_propagate_attrs,
    mock_openai_class,
    mock_langfuse_main,
    mock_langfuse_extract,
    mock_langfuse_context,
    mock_langfuse_parser,
):
    # Make propagate_attributes work as a passthrough context manager
    mock_propagate_attrs.return_value.__enter__ = MagicMock(return_value=None)
    mock_propagate_attrs.return_value.__exit__ = MagicMock(return_value=False)

    # Setup mock Langfuse clients (all module-level singletons)
    for mock_lf_class in [mock_langfuse_main, mock_langfuse_extract, mock_langfuse_context, mock_langfuse_parser]:
        mock_lf_instance = MagicMock()
        mock_lf_class.return_value = mock_lf_instance

    # 1. Setup Mock OpenAI client
    mock_openai_client = MagicMock()
    mock_openai_class.return_value = mock_openai_client

    # Mock for chat.completions.create (used by image_parser and contextualization_agent)
    mock_chat_completion_1 = MagicMock()
    mock_chat_completion_1.choices = [
        MagicMock(message=MagicMock(content="Original Contract: Transcribed text clause 1, 2, 3."))
    ]
    mock_chat_completion_1.usage = MagicMock(prompt_tokens=100, completion_tokens=150, total_tokens=250)

    mock_chat_completion_2 = MagicMock()
    mock_chat_completion_2.choices = [
        MagicMock(message=MagicMock(content="Amendment: Modifies clause 2. Clause 2 is replaced by 2.a."))
    ]
    mock_chat_completion_2.usage = MagicMock(prompt_tokens=120, completion_tokens=80, total_tokens=200)

    mock_chat_completion_3 = MagicMock()
    mock_chat_completion_3.choices = [
        MagicMock(message=MagicMock(
            content="### Contextual Alignment Map\n\n| Original | Amendment | Change |\n|---|---|---|\n| Clause 2 | Section 1 | Modified |"
        ))
    ]
    mock_chat_completion_3.usage = MagicMock(prompt_tokens=300, completion_tokens=150, total_tokens=450)

    # Side effects for OpenAI completions
    mock_openai_client.chat.completions.create.side_effect = [
        mock_chat_completion_1,  # transcription of original
        mock_chat_completion_2,  # transcription of amendment
        mock_chat_completion_3,  # alignment map
    ]

    # Mock for beta.chat.completions.parse (used by extraction_agent)
    mock_parsed_result = ContractChangeOutput(
        sections_changed=["Clause 2"],
        topics_touched=["Payment Terms", "General Terms"],
        summary_of_the_change="Clause 2 was modified to add Subsection 2.a outlining updated payment terms.",
    )
    mock_parsed_completion = MagicMock()
    mock_parsed_completion.choices = [
        MagicMock(message=MagicMock(parsed=mock_parsed_result))
    ]
    mock_parsed_completion.usage = MagicMock(prompt_tokens=600, completion_tokens=100, total_tokens=700)
    mock_openai_client.beta.chat.completions.parse.return_value = mock_parsed_completion

    # Create dummy files
    create_dummy_images()

    try:
        print("Running pipeline execution flow with mocks...")

        # Import run_pipeline AFTER patching to ensure mocks take effect
        from src.main import run_pipeline

        result = run_pipeline(
            original_path="dummy_original.png",
            amendment_path="dummy_amendment.png",
        )
        print("\nPipeline execution succeeded!")
        print("Output:", json.dumps(result.model_dump(), indent=2, ensure_ascii=False))

        # Assertions to ensure calls happened correctly
        assert len(mock_openai_client.chat.completions.create.call_args_list) == 3
        mock_openai_client.beta.chat.completions.parse.assert_called_once()
        print("\nAll assertions passed! The orchestration behaves as expected.")

    finally:
        cleanup_dummy_images()


if __name__ == "__main__":
    test_pipeline_flow()
