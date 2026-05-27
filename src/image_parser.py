import os
import base64
from openai import OpenAI
from langfuse import observe, Langfuse

# Langfuse singleton client for dynamic span updates
langfuse = Langfuse()


def encode_image(image_path: str) -> str:
    """Encodes a local image to base64 string."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_mime_type(image_path: str) -> str:
    """Gets the MIME type of the image based on its extension."""
    ext = os.path.splitext(image_path)[1].lower()
    if ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    elif ext == ".png":
        return "image/png"
    else:
        return "image/jpeg"  # default fallback


@observe(as_type="span")
def parse_contract_image(
    image_path: str,
    contract_type: str,
    openai_client: OpenAI,
) -> str:
    """
    Transcribes the text of a contract page/image using GPT-4o Vision.
    
    The @observe decorator automatically creates a child span under the 
    current trace. OpenAI calls are auto-traced when using the langfuse 
    OpenAI integration.
    
    Args:
        image_path: Path to the image file of the contract.
        contract_type: 'original' or 'amendment' for naming the span.
        openai_client: Initialized OpenAI client.
        
    Returns:
        The transcription text of the contract.
    """
    # Dynamically update the span name and set explicit input
    langfuse.update_current_span(
        name=f"parse_{contract_type}_contract",
        input={"image_path": image_path, "contract_type": contract_type},
    )

    try:
        # Encode image to Base64
        base64_image = encode_image(image_path)
        mime_type = get_mime_type(image_path)

        # System/User Prompts
        system_prompt = (
            "You are an expert legal document transcription system. "
            "Your task is to transcribe all text visible in the contract image with high fidelity. "
            "Maintain the structure, paragraph numbers, headings, formatting, and signatures exactly as they appear. "
            "Do not summarize or skip any parts."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Please transcribe the following {contract_type} contract document in detail.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        },
                    },
                ],
            },
        ]

        # Call OpenAI — generation is auto-traced via the langfuse OpenAI wrapper
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.0,
            name="gpt-4o-vision-transcription",
        )

        transcription = response.choices[0].message.content

        # Update span output
        langfuse.update_current_span(
            output={"transcription_length": len(transcription)}
        )

        return transcription

    except Exception as e:
        langfuse.update_current_span(level="ERROR", status_message=str(e))
        raise
