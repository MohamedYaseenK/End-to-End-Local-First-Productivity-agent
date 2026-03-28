"""
main.py
Entry point — starts the collector loop and saves sessions to the database.
"""

import time
from collector import get_active_window, is_idle
from classifier import classify
from database import init_db, save_session


POLL_INTERVAL = 5  # seconds between each activity check


def run():
    init_db()
    print("Agent running... Press Ctrl+C to stop.")

    current_app = None
    session_start = None

    while True:
        time.sleep(POLL_INTERVAL)

        if is_idle():
            app, title = "idle", "idle"
        else:
            app, title = get_active_window()

        # New session starts when the app changes
        if app != current_app:

            if current_app is not None:
                session_end = time.time()
                category = classify(current_app, current_title)
                save_session(current_app, current_title, category, session_start, session_end)

            current_app = app
            current_title = title
            session_start = time.time()


if __name__ == "__main__":
    run()
