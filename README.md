# ChromaPlot

**ChromaPlot** is a Python application designed for creating high-quality figures of chromatogram data from Cytiva ÄKTA systems. It provides an easy-to-use interface for visualising and analysing your chromatographic data.

## Features

- **Single Mode**: Generate plots of single datasets with customisable options for adding/removing instrument traces, changing line styles, colours, adding shaded areas, and more.
- **Overlay Mode**: Compare multiple datasets by overlaying them on the same plot, with full customisation of each trace. Particularly suited to analytical size-exclusion chromatograms.
- **Analysis**: You can currently add a vertical marker to your plots to measure values at specific curve positions. This a work in progress, and other analytical tools will be added in the future.

A guide on how to use the features of ChromaPlot is provided within the app, however if you have any questions or need help, please reach out to us via [GitHub](https://github.com/beh22/ChromaPlot) or [email](mailto:billyehobbs@gmail.com).

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

ChromaPlot will automatically check for updates each time it is launched. If a new version is available, you will be prompted to update and taken to the [releases](https://github.com/beh22/ChromaPlot/releases) page to download the latest update.

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
