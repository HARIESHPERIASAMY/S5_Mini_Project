import os
import subprocess
import time

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

VIEWS = [
    "start",
    "overview",
    "liverun",
    "findings",
    "agents",
    "history",
    "reports",
    "integrations",
    "settings"
]

RESOLUTIONS = [
    (1440, 900, "1440"),
    (768, 1024, "768")
]

def capture_view(view, width, height, suffix):
    target_file = os.path.join(OUTPUT_DIR, f"{view}_{suffix}.png")
    if os.path.exists(target_file) and os.path.getsize(target_file) > 1000:
        print(f"Already captured {view}_{suffix}.png ({os.path.getsize(target_file)} bytes)")
        return True

    url = f"http://127.0.0.1:5173/?view={view}"
    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={width},{height}",
        f"--screenshot={target_file}",
        url
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        if os.path.exists(target_file) and os.path.getsize(target_file) > 1000:
            print(f"Captured {view}_{suffix}.png ({os.path.getsize(target_file)} bytes)")
            return True
        else:
            print(f"Failed to capture {view}_{suffix}.png: stderr={res.stderr}")
            return False
    except Exception as e:
        print(f"Exception capturing {view}_{suffix}.png: {e}")
        return False

def main():
    print("=== Capturing SentinelMesh Responsive Screenshots (D7) ===")
    total = len(VIEWS) * len(RESOLUTIONS)
    success = 0
    for view in VIEWS:
        for width, height, suffix in RESOLUTIONS:
            if capture_view(view, width, height, suffix):
                success += 1
            time.sleep(0.5)

    print(f"\nResult: {success}/{total} screenshots captured in docs/screenshots/")
    if success == total:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()
