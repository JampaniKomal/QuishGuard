import sys
import os
import shutil
import winshell
import winreg
import subprocess
from PyQt6.QtWidgets import QApplication, QMessageBox

APP_NAME = "QuishGuard"

def uninstall():
    app = QApplication(sys.argv)
    
    reply = QMessageBox.question(None, f"Uninstall {APP_NAME}", 
                               f"Are you sure you want to completely remove {APP_NAME}?",
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    
    if reply == QMessageBox.StandardButton.Yes:
        try:
            # 1. Remove Registry Entry
            try:
                key_path = f"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}"
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            except Exception:
                pass

            # 2. Remove Shortcuts
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, f"{APP_NAME}.lnk")
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            
            # 3. Schedule Silent Self-Destruct
            install_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            batch_file = os.path.join(os.environ["TEMP"], "cleanup_quishguard.bat")

            # Safety check: only ever delete a folder that genuinely looks
            # like a QuishGuard install (named APP_NAME and containing the
            # app's own exe). Without this, a user who installed into an
            # arbitrary folder (or a corrupted argv[0]) could have that
            # entire folder silently wiped by this recursive delete.
            looks_like_install_dir = (
                os.path.basename(os.path.normpath(install_dir)).lower() == APP_NAME.lower()
                and os.path.isfile(os.path.join(install_dir, f"{APP_NAME}.exe"))
            )

            with open(batch_file, "w") as f:
                f.write("@echo off\n")
                # Wait 2 seconds for the uninstaller EXE to close completely
                f.write("timeout /t 2 /nobreak > NUL\n")
                if looks_like_install_dir:
                    # Force delete the folder
                    f.write(f'rmdir /s /q "{install_dir}"\n')
                else:
                    # Path doesn't look like a real install dir - delete only
                    # this app's own files, never the whole folder.
                    f.write(f'del /q "{os.path.join(install_dir, f"{APP_NAME}.exe")}"\n')
                    f.write(f'del /q "{os.path.join(install_dir, "Uninstall.exe")}"\n')
                # Delete this batch file
                f.write('(goto) 2>nul & del "%~f0"\n')
            
            # LAUNCH SILENTLY (No Terminal Window)
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            subprocess.Popen(
                ['cmd', '/c', batch_file],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            QMessageBox.information(None, "Uninstall", f"{APP_NAME} has been removed.")
            sys.exit(0)
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Uninstall failed: {str(e)}")
            sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    uninstall()