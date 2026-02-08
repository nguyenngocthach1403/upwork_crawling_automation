import subprocess, sys, os, venv

def create_venv():
    if not os.path.exists("venv"):
        print("🛠 Tạo virtual environment...")
        venv.create("venv", with_pip=True)

def install_packages():
    print("🔧 Đang cài đặt thư viện...")

    python = os.path.join("venv", "bin", "python") if os.name != "nt" else os.path.join("venv", "Scripts", "python.exe")

    subprocess.check_call([python, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([python, "-m", "pip", "install", "-r", "requirements.txt"])

    print("✅ Cài đặt hoàn tất!")
    print("👉 Chạy: source venv/bin/activate (Linux) hoặc venv\\Scripts\\activate (Windows)")

if __name__ == "__main__":
    create_venv()
    install_packages()
