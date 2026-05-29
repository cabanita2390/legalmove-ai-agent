from langfuse import observe, Langfuse
from langfuse.openai import OpenAI

# Langfuse singleton client for dynamic span updates
langfuse = Langfuse()


class ContextualizationAgent:
    """
    Agent responsible for structural alignment of the original contract and the amendment.
    Identifies which sections of the original contract are modified, added, or deleted
    by the amendment, creating a contextual alignment map.
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
            "You are an expert contract analysis agent. Your goal is to construct a detailed "
            "structural alignment map (Contextual Map) between an original contract and its amendment.\n\n"
            "Review the texts carefully and identify:\n"
            "1. Which clauses, sections, or paragraph numbers of the original contract are referenced or changed by the amendment.\n"
            "2. The nature of the change (e.g., Modification, Deletion, Addition, Clarification).\n"
            "3. A comparison of the old provision vs. the new provision.\n\n"
            "Format your output as a clean, highly structured Markdown report containing a summary "
            "and a clause alignment table.\n"
            "IMPORTANT: Write the entire report in Spanish, including headings, labels, change types, "
            "and all descriptive text."
        )

        user_content = (
            f"### ORIGINAL CONTRACT:\n{original_text}\n\n"
            f"### AMENDMENT:\n{amendment_text}\n\n"
            "Please generate the Contextual Alignment Map. Write all output text in Spanish."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        # OpenAI call is auto-traced as a generation via langfuse.openai wrapper
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.1,
            name="contextualization-gpt-4o",
        )

        alignment_map = response.choices[0].message.content

        # Update span output
        langfuse.update_current_span(
            output={"alignment_map_length": len(alignment_map)}
        )

        return alignment_map
