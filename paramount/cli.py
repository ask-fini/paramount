import sys
import os
import streamlit.web.cli as stcli

# Set Streamlit configuration options via environment variables
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_THEME_BASE"] = "light"
os.environ["STREAMLIT_THEME_PRIMARY_COLOR"] = "#4489bb"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"


def main():
    if len(sys.argv) == 1:
        # User ran only "paramount"
        directory = os.path.dirname(__file__)
        app_path = os.path.join(directory, 'Train.py')
        sys.argv = ["streamlit", "run", app_path] + sys.argv[1:]
        stcli.main()
    else:
        # User had additional cli arguments: "paramount <x>"
        print(f"Running paramount CLI with arguments: {' '.join(sys.argv[1:])}")


if __name__ == "__main__":
    main()
