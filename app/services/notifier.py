from __future__ import annotations

import subprocess
import sys


def send_notification(title: str, message: str, url: str) -> None:
    """Best-effort local notification.

    Linux desktop environments with `notify-send` can show native notifications.
    Other environments fallback to stdout guidance.
    """

    if sys.platform.startswith("linux"):
        try:
            subprocess.run(["notify-send", title, f"{message}\n{url}"], check=False)
            return
        except FileNotFoundError:
            pass

    print(f"[NOTIFICATION] {title}")
    print(message)
    print(f"리포트 열기: {url}")
