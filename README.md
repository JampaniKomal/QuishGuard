# QuishGuard - Advanced Phishing Detection System

QuishGuard is a forensic cybersecurity tool designed to detect, analyze, and unmask malicious QR codes and URLs. Unlike standard scanners, it focuses on Blue Team analysis—revealing redirection chains, hidden scripts, and potential threats before the user opens the link.

## Features

### Smart Detection Engine
- **Multi-Format Scanning**: Drag and drop Images (.png, .jpg) or PDF Documents directly into the application.
- **Batch Processing**: Automatically parses multi-page PDFs to identify and analyze every contained QR code.
- **Heuristic Analysis**: Calculates a "Threat Score" based on redirection depth, IP hostnames, and suspicious keywords to categorize links as Safe, Suspicious, or High Risk.

### Forensic Analysis
- **Redirection Tracing**: Unmasks shortened links (e.g., bit.ly, tinyurl) to reveal the final destination server without visiting it.
- **Defanging**: Automatically converts malicious URLs (e.g., `http://malware.com` becomes `hxxp[:]//malware[.]com`) to prevent accidental execution during analysis.
- **Detailed Logs**: Displays the full hop-by-hop path of any link for forensic auditing.

### Professional Reporting
- **Scan History**: Automatically maintains a local audit trail of all previous scans.
- **Export Reports**: Generates timestamped forensic text reports suitable for evidence or documentation.

### Modern UI
- **Cyber-Brutalist Design**: Features a high-contrast Dark Mode interface built with PyQt6.
- **Privacy First**: All analysis occurs locally on the host machine. No files are uploaded to external cloud servers.

---

## Installation

### For End Users (Recommended)
This project utilizes **Git LFS (Large File Storage)** to host the compiled binary. You do not need Python installed to use this version.

1.  Navigate to the **dist** folder in this repository.
2.  Download the file named **QuishGuard_Setup.exe**.
3.  Run the installer. It will guide you through the setup process and automatically create shortcuts on your Desktop and Start Menu.

### For Developers
If you wish to modify the source code or build the application yourself, follow these steps.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/JampaniKomal/QuishGuard.git
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python main.py
    ```

## Building from Source
To compile the executable and installer from the source code, use the included build script. This script handles the PyInstaller configuration, dependency collection, and installer generation.

```bash
python build_final.py
````

After the build completes, the distribution files will be available in the `dist` directory.

## Project Structure

  - **src/core/**: Contains the scanner engine (OpenCV/PyMuPDF) and analyzer logic.
  - **src/ui/**: Contains the PyQt6 interface logic and styling definitions.
  - **src/utils/**: Helper utilities for history management.
  - **installer/**: Source code for the custom Setup Wizard and Uninstaller.
  - **dist/**: Destination for compiled executables (tracked via LFS).

## Acknowledgments

  - **Gemini (Google):** For providing extensive assistance in the architectural design, debugging, and development of the application logic and user interface.
  - **QtAwesome:** For the FontAwesome icon implementation.
  - **PyMuPDF & OpenCV:** For the core document and image processing capabilities.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Disclaimer

This tool is developed for educational and defensive purposes only. The developers are not responsible for any misuse of this software. Ensure you have proper authorization before analyzing suspicious files or URLs.

## Future Roadmap
- [ ] **Automated Testing:** Implementation of `pytest` suite for core analysis logic.
- [ ] **CI/CD Pipeline:** GitHub Actions workflow for automated linting and building.
- [ ] **Threat Intelligence:** Integration with VirusTotal API for enhanced reputation scoring.