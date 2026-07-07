#!/usr/bin/env python3
import json
import subprocess
import sys

def get_player_status():
    try:
        # status: Playing / Paused / Stopped
        status = subprocess.run(
            ["playerctl", "status"],
            capture_output=True, text=True, timeout=1
        ).stdout.strip()

        if not status or status == "No players found":
            return None

        artist = subprocess.run(
            ["playerctl", "metadata", "artist"],
            capture_output=True, text=True, timeout=1
        ).stdout.strip()

        title = subprocess.run(
            ["playerctl", "metadata", "title"],
            capture_output=True, text=True, timeout=1
        ).stdout.strip()

        player = subprocess.run(
            ["playerctl", "-l"],
            capture_output=True, text=True, timeout=1
        ).stdout.strip().split("\n")[0]

        if not title:
            return None

        text = f"{artist} - {title}" if artist else title
        icon_class = "spotify" if "spotify" in player.lower() else "default"

        return {
            "text": text,
            "class": "paused" if status == "Paused" else "playing",
            "alt": icon_class,
            "tooltip": f"{text} ({status})",
        }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def main():
    # --follow streams a new line every time playerctl detects a change,
    # which is what drives waybar's live updates for this module.
    proc = subprocess.Popen(
        ["playerctl", "--follow", "status"],
        stdout=subprocess.PIPE, text=True, bufsize=1
    )

    # Emit an initial state immediately, then update on every change event
    data = get_player_status()
    print(json.dumps(data if data else {"text": ""}), flush=True)

    for _ in proc.stdout:
        data = get_player_status()
        print(json.dumps(data if data else {"text": ""}), flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
