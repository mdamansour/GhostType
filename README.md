# GhostType

<div align="center">

**Lightweight Offline Voice-to-Text for Any Application**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status: In Development](https://img.shields.io/badge/status-in%20development-orange.svg)]()

[Features](#features) • [How It Works](#how-it-works) • [Installation](#installation) • [Usage](#usage) • [Contributing](#contributing)

</div>

---

## 📖 About

**GhostType** is a portable, privacy-first voice dictation tool that runs entirely offline. Unlike traditional dictation software, GhostType works as a background service that can inject text into *any* application through keyboard simulation—no special integrations needed.

### Why GhostType?

- **🔒 100% Private:** All processing happens locally on your machine. No cloud, no telemetry, no data collection
- **📦 Portable:** Single executable, no installation required. Run from USB, leave no trace
- **🎯 Universal:** Works with any application—browsers, IDEs, legacy software, games
- **⚡ Lightweight:** Uses Vosk for efficient offline speech recognition
- **🎨 Unobtrusive:** Minimal UI with system tray integration

---

## ✨ Features

### Current (v0.1.0-dev)

- **Push-to-Talk Mode:** Hold hotkey to record, release to transcribe
- **Offline Speech Recognition:** Powered by Vosk—no internet required
- **Smart Text Processing:** Auto-capitalization and spacing
- **Voice Commands:** Say "period", "comma", "new line" for punctuation
- **Global Hotkeys:** Trigger from any application

### In Development

- System tray integration
- Visual recording indicator
- Toggle mode (continuous dictation)
- Settings UI
- Multiple language support

---

## 🔧 How It Works

```
[Microphone] → [Vosk Engine] → [Text Sanitizer] → [Keyboard Injection] → [Any App]
```

1. Press configured hotkey (default: `Ctrl+Alt`)
2. Speak your text
3. Release hotkey
4. Text appears in your active window

GhostType uses a producer-consumer architecture to ensure smooth performance, processing audio in the background while keeping the UI responsive.

---

## 🚀 Installation

> **Note:** GhostType is currently in early development (Phase 1). Binaries will be available after Phase 3.

### From Source

**Prerequisites:**
- Python 3.10 or higher
- Microphone

**Steps:**

1. Clone the repository:
```bash
git clone https://github.com/mdamansour/GhostType.git
cd GhostType
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download Vosk model:
   - Visit [Vosk Models](https://alphacephei.com/vosk/models)
   - Download `vosk-model-small-en-us-0.15` (40 MB)
   - Extract to `models/vosk-model-small-en-us-0.15/`

4. Run:
```bash
python src/main.py
```

---

## 💡 Usage

### Basic Dictation

1. Launch GhostType
2. Focus the application you want to type into (Notepad, browser, etc.)
3. Press and hold `Ctrl+Alt`
4. Speak clearly: "Hello world period new line this is a test"
5. Release `Ctrl+Alt`
6. Text appears: "Hello world.\nThis is a test"

### Voice Commands

| Say | Result |
|-----|--------|
| "period" or "full stop" | `.` |
| "comma" | `,` |
| "question mark" | `?` |
| "exclamation mark" | `!` |
| "new line" | Enter key |

### Configuration

Edit `config.json` to customize:
- Hotkeys
- Audio settings
- Typing speed
- Voice command keywords

---

## 🏗️ Development Status

**Current Phase:** Phase 1 - Core Pipeline

GhostType is being developed in three phases:

- **Phase 1 (In Progress):** Core audio → text pipeline
- **Phase 2 (Planned):** Text injection and sanitization
- **Phase 3 (Planned):** UI/UX polish and production release

See [.internal/phases/](.internal/phases/) for detailed development plans.

---

## 🤝 Contributing

Contributions are welcome! This is an open-source project under the MIT license.

**How to Contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Development Setup:**
```bash
git clone https://github.com/mdamansour/GhostType.git
cd GhostType
pip install -r requirements.txt
pytest tests/  # Run tests (when available)
```

---

## 📋 Requirements

- **OS:** Windows 10+, Linux (Ubuntu 20.04+), macOS 11+
- **RAM:** 4 GB (2 GB free)
- **Storage:** 200 MB
- **Audio:** Any microphone (USB or built-in)

---

## 🛡️ Privacy & Security

- **Zero Network Activity:** No internet connection required or used
- **No Data Collection:** Your voice and text never leave your computer
- **No Logging:** Transcribed text is never written to disk
- **Open Source:** Fully auditable code

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Mohamed Amansour**

- LinkedIn: [@mdamansour](https://www.linkedin.com/in/mdamansour/)
- GitHub: [@mdamansour](https://github.com/mdamansour)

---

## 🙏 Acknowledgments

- [Vosk](https://alphacephei.com/vosk/) - Offline speech recognition toolkit
- [SoundDevice](https://python-sounddevice.readthedocs.io/) - Audio I/O library
- [Pynput](https://pynput.readthedocs.io/) - Keyboard and mouse control

---

<div align="center">

**⭐ Star this repo if you find it useful!**

</div>
