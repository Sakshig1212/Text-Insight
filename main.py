
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import BartForConditionalGeneration, BartTokenizer
from keybert import KeyBERT
from fastapi.middleware.cors import CORSMiddleware
# from nltk.tokenize import sent_tokenize # Not used, can be removed or commented out

# --- Model Loading ---
# It's generally good practice to load models once at startup.
# For very large models, you might consider loading them within a FastAPI startup event
# to avoid slowing down the initial module import if the app is part of a larger system.
# However, for a dedicated summarization API, this global loading is common and fine.
try:
    model_name = "facebook/bart-large-cnn"
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)
    kw_model = KeyBERT()
except Exception as e:
    print(f"Error loading models: {e}")
    # You might want to exit or raise a more specific error if models fail to load
    tokenizer = None
    model = None
    kw_model = None

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input model
class SummarizeRequest(BaseModel):
    text: str
    length: str = "medium"  # Options: "short", "medium", "long"
    tone: str = "neutral"   # Options: "neutral", "formal", "informal"
    tone_2: str = "general" # Options: "general", "technical", "creative"

# Length Mapping
LENGTH_MAP = {"short": 50, "medium": 100, "long": 200}

# Tone Mapping
TONE_PROMPTS = {
    "neutral": "Summarize briefly:",
    "formal": "Summarize professionally:",
    "informal": "Summarize casually:",
}
TONE_2_PROMPTS = {
    "general": "",
    "technical": " Focus on technical points.",
    "creative": " Make it imaginative.",
}


# Function to refine summary focus (optional placeholder)
def refine_summary(summary: str) -> str:
    # Example: You could potentially clean up leading/trailing whitespace
    # or perform other minor text processing if needed.
    return summary.strip()

# Summarization function
async def summarize_text_internal(text: str, length_str: str = "medium", tone: str = "neutral", tone_2: str = "general"):
    if not model or not tokenizer:
        raise RuntimeError("Models are not loaded. Cannot summarize.")

    max_length_val = LENGTH_MAP.get(length_str, 100) # Renamed to avoid conflict with 'max_length' param

    # Start with the base tone prompt
    base_prompt = TONE_PROMPTS.get(tone, TONE_PROMPTS["neutral"])

    # Append the tone_2 guidance
    tone_2_guidance = TONE_2_PROMPTS.get(tone_2, TONE_2_PROMPTS["general"])

    # Construct the final prompt for the model
    # The prompt structure is important for how T5 interprets instructions.
    # Example: "Summarize the following text. Focus on a general overview. Text: {actual text}"
    # Or: "Provide a professional summary of the following text. Focus on the technical aspects and details. Text: {actual text}"
    # We need to ensure "Text: " or similar clearly delineates the text to be summarized.
    # Let's refine the prompt structure slightly for better clarity with T5.
    # Typically, instructions come first, then the text.

    # Revised prompt construction:
    # Prompt_Tone1 + " " + Prompt_Tone2 + " Here is the text: " + text
    # This might be too verbose. Let's try to integrate it more naturally.
    # For Flan-T5, it's often good to phrase requests as questions or clear instructions.

    # Option 1: Simpler concatenation (might work, T5 is quite robust)
    # final_instruction = f"{base_prompt} {tone_2_guidance}"
    # full_input_text = f"{final_instruction} Text: {text}"

    # Option 2: More structured prompting (often better for control)
    # Let's modify TONE_PROMPTS to be more like instructions and append tone_2 for specifics
    # TONE_PROMPTS:
    # "neutral": "Summarize this text:"
    # "formal": "Provide a formal summary of this text:"
    # "informal": "Give an informal summary of this text:"
    # TONE_2_PROMPTS:
    # "general": "Ensure the summary is general."
    # "technical": "Focus on technical details in the summary."
    # "creative": "Make the summary creative."

    # Let's stick to your original TONE_PROMPTS structure and append tone_2
    # The key is that the *entire* instruction set (tone1, tone2) precedes the actual text.

    # The original TONE_PROMPTS already end with "the following text:" or similar,
    # so we can append tone_2_guidance before the actual text.
    # Example: "Summarize creatively: <text>"""Summarize technically: <text>""Summarize briefly: <text>" 
    # Let's make sure the prompts are distinct.
    
    # Corrected prompt:
    prompt_prefix = TONE_PROMPTS.get(tone, "Summarize the following text:")
    if tone_2 != "general": # Only add tone_2 if it's not the default "general" to avoid redundancy
        # Modify tone_2_prompts to be phrases that can be appended.
        # e.g., "technical": " focusing on technical details."
        tone_2_specific_prompts = {
            "general": "", # No extra text for general
            "technical": " Emphasize the technical aspects.",
            "creative": " Make it creative and engaging.",
        }
        prompt_prefix += tone_2_specific_prompts.get(tone_2, "")

    final_input_text = prompt_prefix + " " + text



    inputs = tokenizer(final_input_text, return_tensors="pt", max_length=1024, truncation=True) # max_length for input to tokenizer

    # summary_ids = model.generate(
    #     inputs.input_ids,
    #     max_length=max_length_val, # max_length for the generated summary
    #     min_length=max(30, int(max_length_val * 0.3)), # Adjusted min_length logic slightly
    #     length_penalty=2.0 if length_str == "long" else 1.5, # Slightly increased default length penalty
    #     num_beams=5, # Increased beams slightly
    #     temperature=0.7,
    #     repetition_penalty=1.5,
    #     early_stopping=True,
    #     # Consider adding top_k and top_p for diversity if needed
    #     # top_k=50,
    #     # top_p=0.95,
    # )
    summary_ids = model.generate(
    inputs.input_ids,
    max_length=max_length_val,
    min_length=max(30, int(max_length_val * 0.4)),
    length_penalty=1.2,
    num_beams=6,
    temperature=0.9,
    repetition_penalty=1.2,
    top_k=50,
    top_p=0.95,
    early_stopping=True
)


    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return refine_summary(summary)

# Summarize Endpoint
@app.post("/summarize/")
async def summarize(request: SummarizeRequest):
    if not model or not tokenizer: # Check if models loaded
        return {"error": "Summarization model not available."}
    try:
        summary = await summarize_text_internal(request.text, request.length, request.tone, request.tone_2)
        return {"summary": summary}
    except Exception as e:
        # Log the exception e for debugging
        print(f"Error during summarization: {e}")
        return {"error": f"An error occurred during summarization: {str(e)}"}


# Keyword Extraction Endpoint
@app.post("/extract_keywords/")
async def extract_keywords(request: SummarizeRequest):
    if not kw_model:
        return {"error": "Keyword extraction model not available."}
    try:
        keywords = kw_model.extract_keywords(
            request.text,
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            top_n=10
        )

        # DEBUG PRINT
        print("Extracted keywords:", keywords)

        if not keywords:
            return {"keywords": []}
        return {"keywords": [kw[0] for kw in keywords]}
    except Exception as e:
        print(f"Error during keyword extraction: {e}")
        return {"error": f"An error occurred during keyword extraction: {str(e)}"}


# To run this (save as main.py or similar):
# py -3.11 -m uvicorn main:app --reload