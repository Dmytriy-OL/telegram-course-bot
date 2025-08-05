import webbrowser
import threading
import time
import os
from app.web.start_web import run_fastapi
from dotenv import load_dotenv

load_dotenv()


def open_browser():
    time.sleep(1)
    webbrowser.open(os.getenv("BASE_URL"))


if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    run_fastapi()
