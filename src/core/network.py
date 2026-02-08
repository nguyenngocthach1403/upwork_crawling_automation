import socket
import time

def has_internet(timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        return False


def wait_for_internet(check_every=5):
    while not has_internet():
        print("🌐 Mất mạng – chờ khôi phục...")
        time.sleep(check_every)
