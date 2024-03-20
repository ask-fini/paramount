import subprocess
import webbrowser
import threading
import time
from paramount.server.library_functions import load_config

config = load_config()
endpoint = config['api']['endpoint']
port = config['api']['port']
url = f"{endpoint}:{port}"
print(f"Running on url: {url}")


def start_gunicorn():
    gunicorn_command = [
        "gunicorn",
        "--bind", f":{port}",
        "--workers", "1",
        "--threads", "8",
        "--timeout", "0",
        "paramount.server.wsgi:app"
    ]
    subprocess.run(gunicorn_command)


def main():
    # Start gunicorn server in a separate thread
    print("Starting gunicorn server...")
    gunicorn_thread = threading.Thread(target=start_gunicorn)
    gunicorn_thread.start()

    # Wait for a moment to ensure the server starts
    print("Waiting for the server to start...")
    time.sleep(3)  # Adjust the sleep time if necessary

    # Open the browser to the specified localhost port
    print(f"Opening the browser for {url}...")
    webbrowser.open(url)

    # Wait for the gunicorn thread to finish (i.e., until Ctrl+C is pressed)
    try:
        gunicorn_thread.join()
    except KeyboardInterrupt:
        print("Gunicorn server interrupted by user.")
        # Optionally, you can add code here to gracefully shutdown the server if needed


if __name__ == "__main__":
    main()
