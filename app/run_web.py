import webbrowser
import threading
import time
from app.web.start_web import run_fastapi


def open_browser():
    time.sleep(1)  # Трошки почекати, поки сервер стартує
    webbrowser.open("http://192.168.0.103:5000 ")


if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    run_fastapi()
