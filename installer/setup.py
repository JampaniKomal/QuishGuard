import sys
import os
import shutil
import winshell
import winreg  # <--- NEW: Required for Registry
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFileDialog, QProgressBar, 
                             QStackedWidget, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from win32com.client import Dispatch

APP_NAME = "QuishGuard"
APP_VERSION = "1.0.0"
PUBLISHER = "Jampani Komal" # Shows up in Settings
DEFAULT_PATH = os.path.join(os.environ['LOCALAPPDATA'], APP_NAME)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class InstallWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, target_dir):
        super().__init__()
        self.target_dir = target_dir
        
    def run(self):
        try:
            # 1. Prepare
            self.status.emit("Creating directories...")
            self.progress.emit(10)
            if not os.path.exists(self.target_dir):
                os.makedirs(self.target_dir)
            
            # 2. Extract Files
            self.status.emit("Copying application files...")
            self.progress.emit(30)
            
            src_app = resource_path("QuishGuard.exe")
            src_uninst = resource_path("Uninstall.exe")
            dst_app = os.path.join(self.target_dir, "QuishGuard.exe")
            dst_uninst = os.path.join(self.target_dir, "Uninstall.exe")
            
            shutil.copy2(src_app, dst_app)
            self.progress.emit(50)
            shutil.copy2(src_uninst, dst_uninst)
            
            # 3. Registry Registration (The Fix)
            self.status.emit("Registering with Windows...")
            self.progress.emit(70)
            self.register_app(dst_app, dst_uninst)

            # 4. Create Shortcuts
            self.status.emit("Creating shortcuts...")
            self.progress.emit(90)
            desktop = winshell.desktop()
            shell = Dispatch('WScript.Shell')
            
            lnk = shell.CreateShortCut(os.path.join(desktop, f"{APP_NAME}.lnk"))
            lnk.Targetpath = dst_app
            lnk.WorkingDirectory = self.target_dir
            lnk.save()
            
            self.progress.emit(100)
            self.status.emit("Installation Complete.")
            self.finished.emit(True, "Success")
            
        except Exception as e:
            self.finished.emit(False, str(e))

    def register_app(self, exe_path, uninst_path):
        """Writes keys to HKCU so it appears in 'Installed Apps'"""
        try:
            key_path = f"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}"
            # Create the key
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            
            # Write values
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, f"{APP_NAME}")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, PUBLISHER)
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, exe_path)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, self.target_dir)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninst_path}"')
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Registry Error: {e}") # Non-fatal, just won't show in settings

class SetupWizard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} Setup")
        self.setFixedSize(600, 400)
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: white; font-family: 'Segoe UI', sans-serif; }
            QPushButton { background-color: #333; border: 1px solid #555; color: white; padding: 8px 16px; border-radius: 4px; }
            QPushButton:hover { background-color: #444; border-color: #00FF00; }
            QPushButton:disabled { background-color: #222; color: #555; border-color: #333; }
            QLineEdit { background-color: #222; border: 1px solid #444; color: white; padding: 5px; }
            QProgressBar { border: 1px solid #444; text-align: center; background-color: #222; }
            QProgressBar::chunk { background-color: #00FF00; }
            QLabel#Title { font-size: 22px; font-weight: bold; color: #00FF00; }
            QLabel#Desc { font-size: 14px; color: #AAA; }
        """)
        
        self.layout = QVBoxLayout(self)
        self.stack = QStackedWidget()
        
        self.page1 = self.create_page("Welcome", f"This will install {APP_NAME} on your computer.\n\nClick Next to continue.")
        self.page2 = self.create_location_page()
        self.page3 = self.create_install_page()
        self.page4 = self.create_page("Finished", f"{APP_NAME} has been installed.\n\nYou can now find it in your Start Menu or 'Installed Apps'.")

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        self.stack.addWidget(self.page3)
        self.stack.addWidget(self.page4)
        
        self.layout.addWidget(self.stack)
        
        self.btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.close)
        self.btn_next = QPushButton("Next >")
        self.btn_next.clicked.connect(self.next_page)
        
        self.btn_layout.addWidget(self.btn_cancel)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_next)
        self.layout.addLayout(self.btn_layout)
        
    def create_page(self, title_text, desc_text):
        p = QWidget()
        l = QVBoxLayout(p)
        title = QLabel(title_text); title.setObjectName("Title")
        desc = QLabel(desc_text); desc.setObjectName("Desc"); desc.setWordWrap(True)
        l.addStretch(); l.addWidget(title); l.addWidget(desc); l.addStretch()
        return p

    def create_location_page(self):
        p = QWidget()
        l = QVBoxLayout(p)
        title = QLabel("Installation Location"); title.setObjectName("Title")
        self.path_edit = QLineEdit(DEFAULT_PATH)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self.path_edit.setText(QFileDialog.getExistingDirectory(self, "Select Folder") or self.path_edit.text()))
        h = QHBoxLayout(); h.addWidget(self.path_edit); h.addWidget(browse_btn)
        l.addStretch(); l.addWidget(title); l.addLayout(h); l.addStretch()
        return p

    def create_install_page(self):
        p = QWidget()
        l = QVBoxLayout(p)
        title = QLabel("Installing..."); title.setObjectName("Title")
        self.status_label = QLabel("Preparing..."); self.status_label.setObjectName("Desc")
        self.progress = QProgressBar(); self.progress.setValue(0)
        l.addStretch(); l.addWidget(title); l.addWidget(self.status_label); l.addWidget(self.progress); l.addStretch()
        return p

    def next_page(self):
        idx = self.stack.currentIndex()
        if idx == 0: self.stack.setCurrentIndex(1)
        elif idx == 1:
            self.stack.setCurrentIndex(2)
            self.run_installation()
        elif idx == 3: self.close()

    def run_installation(self):
        self.btn_next.setEnabled(False); self.btn_cancel.setEnabled(False)
        target = self.path_edit.text()
        # Always install into an APP_NAME-named subfolder, even if the user
        # browsed to an unrelated existing folder (e.g. their Desktop). The
        # uninstaller deletes this folder by name later, so it must never be
        # allowed to be a folder the user did not intend to have wiped.
        if os.path.basename(os.path.normpath(target)).lower() != APP_NAME.lower():
            target = os.path.join(target, APP_NAME)
        self.worker = InstallWorker(target)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.status.connect(self.status_label.setText)
        self.worker.finished.connect(self.done)
        self.worker.start()

    def done(self, success, msg):
        if success:
            self.stack.setCurrentIndex(3)
            self.btn_next.setText("Finish"); self.btn_next.setEnabled(True); self.btn_cancel.setVisible(False)
        else:
            QMessageBox.critical(self, "Error", msg); self.btn_next.setEnabled(True); self.stack.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wiz = SetupWizard()
    wiz.show()
    sys.exit(app.exec())