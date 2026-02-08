import subprocess
import time
import os

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR_BASE = r"D:/Project/Data Engineer/upwork_crawling/profiles/"
DEBUG_PORT = 9222

def init_chrome_profile(profile_dir: str):
    os.makedirs(PROFILE_DIR_BASE  + profile_dir, exist_ok=True)

    cmd = [
        CHROME_PATH,
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={PROFILE_DIR_BASE  + profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-blink-features=AutomationControlled"
    ]

    subprocess.Popen(cmd, shell=False)
    time.sleep(5)  # đợi chrome mở xong

if __name__ == "__main__":
    init_chrome_profile("acc_0001")
