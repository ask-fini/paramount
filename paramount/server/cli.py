import subprocess
import webbrowser
import sys
import time


def main():
    try:
        # Start gunicorn server with the specified arguments
        gunicorn_command = [
            "gunicorn",
            "--bind", ":9001",
            "--workers", "1",
            "--threads", "8",
            "--timeout", "0",
            "paramount.server.wsgi:app"
        ]
        print("Starting gunicorn server...")
        subprocess.Popen(gunicorn_command)

        # Wait for a moment to ensure the server starts
        print("Waiting for the server to start...")
        time.sleep(3)  # Adjust the sleep time if necessary

        # Open the browser to the specified localhost port
        print("Opening the browser...")
        webbrowser.open("http://localhost:9001")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
