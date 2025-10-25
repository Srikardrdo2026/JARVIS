import os
import csv
import sys
from datetime import datetime
from speech import say, record_audio
from app_launcher import open_app, close_app
from file_scanner import scan_directories  # Import from file_scanner.py
import ai_handler  # Import the n8n-based AI handler module

# Voice commands that will trigger shutdown
SHUTDOWN_COMMANDS = ["power off", "shutdown", "quit", "exit", "stop listening", "turn off"]

# Define a constant for the "open " literal
OPEN_COMMAND_PREFIX = "open "

def handle_time_query(query):
    """Handle time queries."""
    if "the time" in query:
        time = datetime.now().strftime("%H:%M:%S")
        say(f"The time is {time}")
        return True
    return False

def handle_website_query(query):
    """Handle website opening queries."""
    from domain_loader import load_domains, find_best_match, open_website  # Moved imports here
    domains = load_domains(top_n=10000)  # Load domains inside function
    matches = find_best_match(query, domains)
    if matches:
        open_website(matches[0])
        say(f"Opening {matches[0]}")
        return True
    return False

def handle_file_scan_query(query):
    """Handle file scanning queries."""
    if "scan files" in query:
        home = os.path.expanduser('~')
        directories_to_scan = [
            os.path.join(home, 'Documents'),
            os.path.join(home, 'Desktop'),
            os.path.join(home, 'Videos'),
            os.path.join(home, 'Pictures'),
            os.path.join(home, 'Downloads'),
            os.path.join(home, 'Music'),
            os.path.join(os.environ.get('SystemDrive', 'C:'), 'Program Files'),
            os.path.join(os.environ.get('SystemDrive', 'C:'), 'Program Files (x86)'),
            os.environ.get('SystemDrive', 'C:') + '\\',
        ]
        file_types = {'.txt', '.pdf', '.docx', '.xlsx', '.jpg', '.png', '.mp4', '.mp3'}  # Consistent with initialize_file_scan
        output_csv = os.path.join(home, 'file_index.csv')
        num_files_scanned = scan_directories(directories_to_scan, file_types, output_csv)
        say(f"Scanned {num_files_scanned} files and saved the index.")
        print(f"[INFO] Scanned {num_files_scanned} files and saved to {output_csv}")
        return True
    return False

def handle_shutdown(query):
    """Handle shutdown commands."""
    if any(cmd in query for cmd in SHUTDOWN_COMMANDS):
        print("[INFO] Shutting down by voice command.")
        say("Shutting down JARVIS A.I. Goodbye.")
        sys.exit(0)
    return False

def handle_file_or_folder(query):
    """Handle file or folder opening commands."""
    folder_mapping = {
        "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
        "documents": os.path.join(os.path.expanduser("~"), "Documents"),
        "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
        "music": os.path.join(os.path.expanduser("~"), "Music"),
        "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
        "videos": os.path.join(os.path.expanduser("~"), "Videos"),
        "project folder": "C:/Users/srika/Desktop/Project/J.A.R.V.I.S AI",
    }

    query = query.replace("folder", "").strip()

    if query.startswith(OPEN_COMMAND_PREFIX):
        target = query.replace(OPEN_COMMAND_PREFIX, "").strip()
        target_path = folder_mapping.get(target.lower(), target)

        if os.path.exists(target_path):
            try:
                os.startfile(target_path)
                if os.path.isfile(target_path):
                    say(f"Opening file {os.path.basename(target_path)}")
                    print(f"[INFO] Opened file: {target_path}")
                elif os.path.isdir(target_path):
                    say(f"Opening folder {os.path.basename(target_path)}")
                    print(f"[INFO] Opened folder: {target_path}")
                return True
            except Exception as e:
                say("Sorry, I couldn't open it.")
                print(f"[ERROR] Failed to open {target_path}: {e}")
                return False
        else:
            say("The specified file or folder does not exist.")
            print(f"[ERROR] File or folder not found: {target_path}")
            return False
    return False

def handle_app_commands(query):
    """Handle app launcher and closer commands."""
    if query.startswith("open ") and open_app(query):
        return True
    if query.startswith("close ") and close_app(query):
        return True
    return False

def handle_code_query(query):
    """Handle code generation or debugging queries."""
    if "debug code" in query or "write code" in query:
        try:
            ai_handler.handle_code_query(query)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to process code query: {e}")
            say("Sorry, I couldn't assist with the code.")
            return False
    return False

def handle_text_ai_query(query):
    """Handle text-based AI queries."""
    if "using artificial intelligence" in query:
        try:
            ai_handler.handle_text_query(query)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to process text AI query: {e}")
            say("Sorry, I encountered an error while processing your AI request.")
            return False
    return False

def handle_voice_to_text_query(query):
    """Handle voice-to-text transcription queries."""
    if "transcribe audio" in query:
        try:
            temp_audio_path = os.path.join(os.path.expanduser('~'), 'temp_audio.wav')
            record_audio(temp_audio_path, duration=5)
            ai_handler.handle_voice_to_text(temp_audio_path)
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to transcribe audio: {e}")
            say("Sorry, I couldn't transcribe the audio.")
            return False
    return False

def get_image_path_from_query(query, base_dir=os.path.join(os.path.expanduser('~'), 'Pictures')):
    """Extract the image filename from the query and return the full path."""
    query_parts = query.lower().split("image")
    if len(query_parts) > 1:
        image_name = query_parts[-1].strip()
        if not image_name.endswith(('.jpg', '.jpeg', '.png')):
            image_name += '.jpg'
        image_path = os.path.join(base_dir, image_name)
        if os.path.exists(image_path):
            return image_path
    return None

def handle_image_to_text_query(query):
    """Handle image-to-text extraction queries."""
    if "extract text from image" in query:
        image_path = get_image_path_from_query(query)
        if not image_path:
            say("Please specify a valid image file in your Pictures directory.")
            print("[ERROR] Image file not found.")
            return False
        try:
            ai_handler.handle_image_to_text(image_path)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to extract text from image: {e}")
            say("Sorry, I couldn't extract text from the image.")
            return False
    return False

def handle_multimodal_query(query):
    """Handle multimodal (e.g., image captioning) queries."""
    if "describe image" in query:
        image_path = get_image_path_from_query(query)
        if not image_path:
            say("Please specify a valid image file in your Pictures directory.")
            print("[ERROR] Image file not found.")
            return False
        try:
            ai_handler.handle_multimodal_image_caption(image_path)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to describe image: {e}")
            say("Sorry, I couldn't describe the image.")
            return False
    return False

def handle_command(query):
    """Handle and dispatch the user's spoken command."""
    if not query:
        return False

    query = query.lower().strip()
    print(f"[DEBUG] Processing query in command_handler.py: '{query}'")

    if handle_shutdown(query):
        return True
    if handle_file_or_folder(query):
        return True
    if handle_app_commands(query):
        return True
    if handle_text_ai_query(query):
        return True
    if handle_voice_to_text_query(query):
        return True
    if handle_image_to_text_query(query):
        return True
    if handle_multimodal_query(query):
        return True
    if handle_code_query(query):
        return True
    if handle_website_query(query):
        return True
    if handle_file_scan_query(query):
        return True
    if handle_time_query(query):
        return True

    say("I'm not sure what you mean. Please try again.")
    print(f"[ERROR] Unknown command: '{query}'")
    return False

def initialize_file_scan():
    """Scans specific folders like Downloads and Desktop during initialization."""
    home = os.path.expanduser('~')
    directories_to_scan = [
        os.path.join(home, 'Documents'),
        os.path.join(home, 'Desktop'),
        os.path.join(home, 'Videos'),
        os.path.join(home, 'Pictures'),
        os.path.join(home, 'Downloads'),
        os.path.join(home, 'Music'),
    ]
    file_types = {'.txt', '.pdf', '.docx', '.xlsx', '.jpg', '.png', '.mp4', '.mp3'}
    output_csv = os.path.join(home, 'file_index.csv')

    say("Scanning specific folders on startup...")
    try:
        num_files_scanned = scan_directories(directories_to_scan, file_types, output_csv)
        print(f"[INFO] Scanned {num_files_scanned} files and saved to {output_csv}")
        say(f"Startup file scan complete. {num_files_scanned} files indexed.")
    except Exception as e:
        print(f"[ERROR] Failed to scan files: {e}")
        say("An error occurred while scanning files.")