import sys
from speech import say
from command_handler import handle_command as process_command
from wake_listener import listen_for_wake_word

if __name__ == "__main__":
    try:
        from command_handler import initialize_file_scan

        # Trigger file scan on startup
        initialize_file_scan()

        say("Hello, I am JARVIS A.I.")
        listen_for_wake_word()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        say("Goodbye")
        sys.exit(0)
        
        
'''
for n8n. this command in terminal : docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
'''