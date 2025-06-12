import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("main.py"):
            print("\n🔁 Detected change, re-running app...\n")
            subprocess.run(["python", "main.py"])


if __name__ == "__main__":
    print("👀 Watching for changes in main.py...\n")
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
