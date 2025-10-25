import requests
import os
from speech import say

# n8n webhook URLs (replace with your actual webhook URLs from n8n)
N8N_TEXT_QUERY_URL = "http://localhost:5678/webhook/text-query-workflow"
N8N_VOICE_TO_TEXT_URL = "http://localhost:5678/webhook/voice-to-text-workflow"
N8N_IMAGE_TO_TEXT_URL = "http://localhost:5678/webhook/image-to-text-workflow"
N8N_IMAGE_CAPTION_URL = "http://localhost:5678/webhook/image-caption-workflow"
N8N_CODE_QUERY_URL = "http://localhost:5678/webhook/code-query-workflow"

def call_n8n_workflow(webhook_url, data=None, files=None):
    """Helper function to call an n8n workflow."""
    try:
        response = requests.post(webhook_url, json=data if not files else None, files=files)
        response.raise_for_status()
        return response.json().get("result", "No result returned from n8n")
    except Exception as e:
        print(f"[ERROR] Failed to call n8n workflow: {e}")
        return None

def handle_code_query(prompt):
    """Handle code generation or debugging via n8n workflow."""
    data = {"prompt": prompt}
    result = call_n8n_workflow(N8N_CODE_QUERY_URL, data)
    if result:
        print(result)
        say(f"Code assistance: {result}")
        return result
    say("Sorry, I couldn't assist with the code.")
    return None

def handle_text_query(prompt):
    """Handle text-based AI queries via n8n workflow."""
    data = {"prompt": prompt}
    result = call_n8n_workflow(N8N_TEXT_QUERY_URL, data)
    if result:
        print(result)
        say(result)
        return result
    say("Sorry, I couldn't process the AI request.")
    return None

def handle_voice_to_text(audio_path):
    """Handle voice-to-text transcription via n8n workflow."""
    try:
        with open(audio_path, "rb") as audio_file:
            files = {"audio": audio_file}
            result = call_n8n_workflow(N8N_VOICE_TO_TEXT_URL, files=files)
        if result:
            print(result)
            say(f"I heard: {result}")
            return result
    except Exception as e:
        print(f"[ERROR] Voice to text failed: {e}")
    say("Sorry, I couldn't transcribe the audio.")
    return None

def handle_image_to_text(image_path):
    """Handle image-to-text extraction via n8n workflow."""
    try:
        with open(image_path, "rb") as image_file:
            files = {"image": image_file}
            result = call_n8n_workflow(N8N_IMAGE_TO_TEXT_URL, files=files)
        if result:
            print(result)
            say(f"Text in image: {result}")
            return result
    except Exception as e:
        print(f"[ERROR] Image to text failed: {e}")
    say("Sorry, I couldn't extract text from the image.")
    return None

def handle_multimodal_image_caption(image_path):
    """Handle image captioning via n8n workflow."""
    try:
        with open(image_path, "rb") as image_file:
            files = {"image": image_file}
            result = call_n8n_workflow(N8N_IMAGE_CAPTION_URL, files=files)
        if result:
            print(result)
            say(f"Image description: {result}")
            return result
    except Exception as e:
        print(f"[ERROR] Image captioning failed: {e}")
    say("Sorry, I couldn't describe the image.")
    return None