'''
ChromaPlot Version 1.0.0
Authors: Billy Hobbs and Felipe Ossa
© 2024 Billy Hobbs. All rights reserved.
'''

import requests
import sys
from PyQt5.QtWidgets import QMessageBox

CURRENT_VERSION = "1.0.0"
GITHUB_API_URL = "https://api.github.com/repos/beh22/ChromaPlot/releases/latest"

def check_for_updates():
    try:
        response = requests.get(GITHUB_API_URL)
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
        # Open the GitHub release page in the default browser
        import webbrowser
        webbrowser.open(download_url)
        sys.exit()
