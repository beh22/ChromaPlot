'''
ChromaPlot Version 0.1.0
Authors: Billy Hobbs and Felipe Ossa
© 2024 Billy Hobbs. All rights reserved.
'''

import subprocess
import webbrowser
import requests
import sys
from PyQt5.QtWidgets import QMessageBox

GITHUB_API_URL = "https://api.github.com/repos/beh22/ChromaPlot/releases/latest"
GITHUB_TOKEN = "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"

def check_for_updates(CURRENT_VERSION):
    try:
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}"
        }
        response = requests.get(GITHUB_API_URL, headers=headers)
        response.raise_for_status()
        latest_release = response.json()

        latest_version = latest_release["tag_name"]

        if latest_version > CURRENT_VERSION:
            return latest_release
        return None

    except Exception as e:
        print(f"Error checking for updates: {e}")
        return None

def prompt_for_update(latest_release):
    download_url = latest_release["html_url"]

    reply = QMessageBox.question(
        None, "Update Available",
        f"A new version {latest_release['tag_name']} is available. Would you like to update?",
        QMessageBox.Yes | QMessageBox.No
    )

    if reply == QMessageBox.Yes:
        try:
            webbrowser.open_new_tab(download_url)
        except Exception as e:
            print(f"Error opening the web browser: {e}")
            if sys.platform == 'darwin':
                try:
                    subprocess.run(['open', download_url])
                except Exception as e:
                    print(f"Failed to open with fallback method on macOS: {e}")
                    QMessageBox.critical(None, "Error", "Failed to open the web browser. Please visit the GitHub page manually.")
            else:
                QMessageBox.critical(None, "Error", "Failed to open the web browser. Please visit the GitHub page manually.")                  
        
        sys.exit()