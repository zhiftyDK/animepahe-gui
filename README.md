# AnimePahe GUI

[![Build Status](https://github.com/zhiftyDK/animepahe-gui/workflows/Build%20and%20Release/badge.svg)](https://github.com/zhiftyDK/animepahe-gui/actions)
[![Release](https://img.shields.io/github/v/release/zhiftyDK/animepahe-gui?include_prereleases)](https://github.com/zhiftyDK/animepahe-gui/releases)
[![License](https://img.shields.io/github/license/zhiftyDK/animepahe-gui)](LICENSE)

A command-line gui interface for downloading anime episodes from AnimePahe.si with support for searching animes and merging audiotracks after download.

## ⚠️ Beta Notice

This is a **beta version** and may encounter issues during operation. The current version has the following limitations:
- Some edge cases may cause unexpected behavior

## 📋 Features

- **Download Support**: Download anime episodes directly through the GUI tool with real-time progress tracking, speed monitoring, and ETA display
- **Searchable Content**: Search for animes with a search string, it done using rapidfuzz.
- **MKV Audio Track Merging**: When multiple languages are selected you can merge all audio tracks into one mkv file. Allowing for langauge selection in certain video players like Windows Media Player.
**Self-Updating**: Automatically update to the latest version when running the app

## 🚀 Installation

### Windows
1. Download the latest `animepahe-gui.exe` from the [Releases](https://github.com/zhiftyDK/animepahe-gui/releases) page
2. Place the executable in your desired directory
3. Open Command Prompt or PowerShell in that directory or double click the executable

### Building from Source

#### Windows/Linux
```bash
git clone https://github.com/zhiftyDK/animepahe-gui.git
cd animepahe-gui
pip install -r requirements.txt
pyinstaller --onefile ^
    --name animepahe ^
    --console ^
    --add-binary "./resources/windows/animepahe-cli-beta.exe;." ^
    --add-binary "./resources/windows/ffmpeg.exe;." ^
    animepahe.py
```

### Platform Support
- **Windows**: Fully supported with native executable
- **Linux**: Potential future support under consideration

### Dependencies
- **animepahe-cli-beta.exe**: [The anime downloader cli tool](https://github.com/Danushka-Madushan/animepahe-cli)
- **ffmpeg.exe**: FFmpeg is used to merge audio tracks from videos into multilingual mkv.
- **Python Dependencies**: questionary, bs4, rapidfuzz, requests, pyinstaller

### Build Requirements
- Python 3.11 or higher
- FFmpeg
- Animepahe-Cli
- requirements.txt

## 🐛 Known Issues
- Language selection may not work with every anime, as availability depends on the source content
- Network timeouts may occur with slow connections
- Large batch downloads may consume significant system resources
- Update feature requires internet connection and appropriate permissions
- Some animes may not download: [Issue 43 animepahe-cli](https://github.com/Danushka-Madushan/animepahe-cli/issues/43)

## 🚧 Upcoming Features
- **Improved ui**: Converting this project to a proper gui with Tkinter

## 🧑‍🏭 Contributors
Many thanks to [@Danushka-Madushan](https://github.com/Danushka-Madushan) for creating the [animepahe-cli](https://github.com/Danushka-Madushan/animepahe-cli) making this project possible. 

## 📄 License

This project is licensed under the MIT license.  
You are allowed to use this software commercially or personally, you may modify, redistribute, or create derivative works.
See the [LICENSE](LICENSE) file for details.

The animepahe-cli by [Danushka-Madushan](https://github.com/Danushka-Madushan/animepahe-cli) is under a seperate [LICENSE](https://github.com/Danushka-Madushan/animepahe-cli/blob/main/LICENSE).

## ⚖️ Disclaimer

This tool is for educational purposes only. Users are responsible for complying with AnimePahe.ru's terms of service and applicable copyright laws. The developers do not condone piracy or copyright infringement.

## 🔗 Links

- [AnimePahe](https://animepahe.si) - Source website (primary). Legacy: https://animepahe.ru
- [Issues](https://github.com/zhiftyDK/animepahe-gui/issues) - Bug reports and feature requests
- [Releases](https://github.com/zhiftyDK/animepahe-gui/releases) - Download latest versions