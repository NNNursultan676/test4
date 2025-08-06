
#!/usr/bin/env python3
import os
import sys
import threading
import time

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Change to the script directory
os.chdir(current_dir)

def run_bot():
    """Run Telegram bot"""
    try:
        from bot import main
        print("Starting Telegram bot...")
        main()
    except Exception as e:
        print(f"Error running bot: {e}")

def run_web_app():
    """Run Flask web application"""
    try:
        from app import app
        print("Starting web application on http://0.0.0.0:5000...")
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Error running web app: {e}")

if __name__ == '__main__':
    print("Starting both Telegram bot and web application...")
    
    # Start bot in separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Give bot time to start
    time.sleep(2)
    
    # Start web app in main thread
    run_web_app()
