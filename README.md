# ChromaPlot

**ChromaPlot** is a Python application designed for creating high-quality figures of chromatogram data from Cytiva ÄKTA systems. It provides an easy-to-use interface for visualising and analysing your chromatographic data.

## Features

- **Single Mode**: Generate plots of single datasets with customisable options for adding/removing instrument traces, changing line styles, colours, adding shaded areas, and more.
- **Overlay Mode**: Compare multiple datasets by overlaying them on the same plot, with full customisation of each trace. Particularly suited to analytical size-exclusion chromatograms.
- **Analysis**: You can currently add a vertical marker to your plots to measure values at specific curve positions. This a work in progress, and other analytical tools will be added in the future.

A guide on how to use the features of ChromaPlot is provided within the app, however if you have any questions or need help, please reach out to us via [GitHub](https://github.com/beh22/ChromaPlot/issues) or [email](mailto:billyehobbs@gmail.com).

## Installation

To intall ChromaPlot, follow these steps:

### For Windows:

1. Download the latest `.exe` file from the [releases](https://github.com/beh22/ChromaPlot/releases) section.
2. Run the installer and follow the on-screen instructions.
3. Once installed, you can start ChromaPlot from the Start Menu or desktop shortcut.

### For macOS:

1. Download the latest `.dmg` file from the [releases](https://github.com/beh22/ChromaPlot/releases) section.
2. Open the `.dmg` file and drag the ChromaPlot icon to your Applications folder.
3. Open ChromaPlot from the Applications folder or Launchpad.

**Important Information for macOS Users**: Since ChromaPlot is not signed with an Apple-issued certificate, you may encounter a warning when attempting to open the application. This is because Apple cannot verify that the app is from a trusted developer.

**To Open ChromaPlot:**

1. After downloading the `.dmg` file, double-click it to open.
2. Drag the ChromaPlot app to your Applications folder.
3. Attempt to open the app by double-clicking it.
4. If you see a warning stating that the app is from an unidentified developer, follow these steps:
   - Go to **System Preferences** > **Security & Privacy** > **General**.
   - Click the "Open Anyway" button near the message about ChromaPlot.
   - Confirm that you want to open the app in the dialog box that appears.

**Disclaimer**: While we have taken steps to ensure that ChromaPlot is safe and secure, the app has not been officially notarized by Apple. If you have any concerns about security, feel free to review the source code available in this repository or run from the source code as described below.

**Why This Happens**: Apple's security system, Gatekeeper, protects users by ensuring that only apps from identified developers are installed without extra steps. To become an identified developer, a paid Apple Developer account is required, which is not feasible for every open-source project.

### From Source:

If you would prefer to run ChromaPlot from the source code:

1. Clone this repository:
   ```bash
   git clone https://github.com/beh22/ChromaPlot.git
   ```
2. Navigate to the project directory:
   ```bash
   cd ChromaPlot
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## Updating ChromaPlot

ChromaPlot will automatically check for updates each time it is launched. If a new version is available, you will be prompted to update and taken to the [releases](https://github.com/beh22/ChromaPlot/releases) page to download the latest update. Download the latest version as above and when prompted, choose to 'Replace' the existing install.

## Contributing

Contributions are welcome! If you'd like to contribute to ChromaPlot, please follow these steps:

1. Fork this repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-branch-name
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to your fork:
   ```bash
   git push origin feature-branch-name
   ```
5. Create a pull request, and we'll review your changes.

## Licensing and Copyright

This repository contains the source code for ChromaPlot, which is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute the source code under the terms of this license.

**Note**: The ChromaPlot executable, branding, and logos are copyrighted and are not covered by the open-source license. The use of these elements is restricted and may require a separate license.

For more information on licensing and usage, please contact Billy at [billyehobbs@gmail.com](mailto:billyehobbs@gmail.com).
