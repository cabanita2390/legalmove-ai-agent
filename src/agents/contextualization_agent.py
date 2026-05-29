from langfuse import observe, Langfuse
from langfuse.openai import OpenAI
import openai
from pydantic import ValidationError

# Langfuse singleton client for dynamic span updates
langfuse = Langfuse()


class ContextualizationAgent:
    """
    Agent responsible for structural alignment of the original contract and the amendment.
    Builds a navigable contextual map (section IDs, cross-references, structural change types)
    without listing or summarizing commercial or legal modifications.
    """

    def __init__(self, openai_client: OpenAI = None):
        self.client = openai_client or OpenAI()

    @observe(as_type="span", name="contextualization_agent")
    def align_contracts(self, original_text: str, amendment_text: str) -> str:
        """
        Compares the original contract and the amendment, aligning the modified clauses.
        
        Args:
            original_text: Transcribed text of the original contract.
            amendment_text: Transcribed text of the amendment.
            
        Returns:
            A structured Markdown text representing the contextual mapping between the two documents.
        """
        # Set explicit input (avoid leaking all function args)
        langfuse.update_current_span(
            input={
                "original_text_length": len(original_text),
                "amendment_text_length": len(amendment_text),
            }
        )

        system_prompt = (
            "You are an expert contract structural analysis agent. Your ONLY responsibility is to "
            "construct a structural alignment map (Contextual Map) between an original contract and its amendment.\n\n"
            "Your job is to STRUCTURE and NAVIGATE the documents — not to analyze or summarize their commercial content.\n\n"
            "Review the texts and produce:\n"
            "1. Which clauses, sections, or paragraph numbers of the original contract are referenced, "
            "touched, or affected by the amendment.\n"
            "2. The structural type of each link (Modification, Deletion, Addition, Clarification) — label only, "
            "no content analysis.\n"
            "3. Cross-references between amendment passages and original contract locations.\n\n"
            "STRICT PROHIBITIONS — do NOT:\n"
            "- List, describe, or summarize commercial or legal modifications (e.g., price changes, penalty terms, "
            "new obligations).\n"
            "- Compare or quote the old provision vs. the new provision.\n"
            "- Include amounts, dates, percentages, or any substantive before/after content.\n"
            "- Write executive summaries of what changed in business terms.\n\n"
            "Format your output as clean Markdown with a clause alignment table "
            "(section ID, structural change type, cross-reference).\n"
            "IMPORTANT: Write the entire report in Spanish, including headings, labels, and change types."
        )

        user_content = (
            f"### ORIGINAL CONTRACT:\n{original_text}\n\n"
            f"### AMENDMENT:\n{amendment_text}\n\n"
            "Generate the structural Contextual Alignment Map only. Do not summarize commercial modifications. "
            "Write all output text in Spanish."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        # OpenAI call is auto-traced as a generation via langfuse.openai wrapper
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.0,
                name="gpt-4o-vision-transcription",
            )
        except (openai.RateLimitError, openai.APIError, openai.TimeoutError, ValidationError) as e:
            langfuse.update_current_span(error=str(e))
            raise

        alignment_map = response.choices[0].message.content

        # Update span output
        langfuse.update_current_span(
            output={"alignment_map_length": len(alignment_map)}
        )

        return alignment_map
