import requests

def check_internet():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.RequestException:
        return False

print("✅ Online" if check_internet() else "❌ Offline")
