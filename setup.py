import subprocess
import sys
import os

def create_and_setup_venv():
    venv_folder = ".venv"
    python_executable = sys.executable

    # Tworzenie wirtualnego środowiska
    if not os.path.exists(venv_folder):
        print(f"Tworzenie wirtualnego środowiska: {venv_folder}")
        subprocess.check_call([python_executable, "-m", "venv", venv_folder])
    else:
        print(f"Wirtualne środowisko {venv_folder} już istnieje.")

    # Aktywacja środowiska wirtualnego
    if os.name == "nt":  # Windows
        pip_executable = os.path.join(venv_folder, "Scripts", "pip.exe")
    else:  # Linux/Mac
        pip_executable = os.path.join(venv_folder, "bin", "pip")

    # Instalacja zależności z requirements.txt
    print("Instalacja bibliotek z requirements.txt...")
    try:
        subprocess.check_call([pip_executable, "install", "-r", "requirements.txt"])
        print("Biblioteki zostały pomyślnie zainstalowane.")
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas instalacji zależności: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_and_setup_venv()