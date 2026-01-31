# GhostType: Technical Specification & Architecture Document

**Version:** 1.0.0 (Draft)
**Type:** Desktop Application (Portable / Background Service)
**License:** Open Source (MIT Recommended)

---

## 1. Executive Summary

**GhostType** is a lightweight, portable, offline voice-to-text utility. Unlike standard dictation software, GhostType runs as a "sidecar" background process, allowing users to inject text into *any* application (Browsers, IDEs, Legacy Software) via keyboard simulation. It requires no installation, leaves no trace, and guarantees 100% privacy by processing all audio locally.

---

## 2. Architectural Design

To ensure **maintainability** and **upgradability**, we will use a **Modular Layered Architecture** driven by an **Event-Driven (Producer-Consumer)** flow. This avoids "spaghetti code" where the GUI freezes while the AI is thinking.

### 2.1 The Core Design Pattern: Producer-Consumer

The application relies on a thread-safe **Queue** to decouple the *Audio Recording* (Fast) from the *AI Processing* (Slower).

1. **Input Producer (Audio Thread):** Captures raw bytes from the microphone. Puts them into `AudioQueue`.
2. **Processor Consumer (Worker Thread):** Takes bytes from `AudioQueue`, feeds them to Vosk, and produces text. Puts text into `TextQueue`.
3. **Action Consumer (Main/UI Thread):** Takes text from `TextQueue`, sanitizes it, and injects it into the OS.

### 2.2 Component Diagram

```mermaid
graph TD
    User((User)) -->|Hotkey| InputMgr[Input Manager]
    InputMgr -->|Start/Stop| Controller[Core Controller]

    subgraph "Core Application"
        Controller --> Audio[Audio Capture Service]
        Controller --> Engine[Speech Engine (Vosk)]
        Controller --> UI[Tray & Overlay UI]
        
        Audio -->|Raw Bytes| Queue((Queue))
        Queue --> Engine
        Engine -->|Raw Text| Sanitizer[Text Sanitizer]
        Sanitizer -->|Clean Text| Injector[Key Injector]
    end

    Injector -->|Simulated Keystrokes| ActiveApp[Active Window (Notepad/Browser)]
    UI -->|Visual Feedback| User

```

---

## 3. Technology Stack

| Component | Technology | Rationale |
| --- | --- | --- |
| **Language** | **Python 3.10+** | Rapid development, rich AI ecosystem, easy to package. |
| **Speech Engine** | **Vosk** | Best-in-class for offline, lightweight CPU inference. |
| **Audio I/O** | **SoundDevice** | Lower latency and fewer dependencies than PyAudio. |
| **Input Hooks** | **Pynput** | Cross-platform global hotkey detection. |
| **GUI / Tray** | **Pystray** + **Tkinter** | Pystray for system tray; Tkinter for lightweight overlay. |
| **Packaging** | **PyInstaller** | Bundles Python + dependencies + Models into one `.exe`. |
| **Config** | **JSON** | Human-readable configuration for hotkeys and preferences. |

---

## 4. Functional Specifications

### 4.1. Core Modes

1. **Push-to-Talk (PTT):**
* *Behavior:* Recording active *only* while the user holds the trigger key.
* *Use Case:* Short commands, quick replies.


2. **Toggle Mode (Continuous):**
* *Behavior:* Double-press Trigger to start; single press to stop.
* *Use Case:* Long-form dictation (writing essays/emails).



### 4.2. The "Sanitizer" Logic (Smart Formatting)

The raw output from Vosk is lowercase and unpunctuated. The `Sanitizer` module must apply the following rules *before* typing:

* **Auto-Capitalization:** The first character of a session is capitalized.
* **Sticky Spacing:** Automatically insert a leading space if the previous injected character was not a newline or start-of-sentence.
* **Keyword Replacements:**
* "new line"  `\n` (Enter Key)
* "full stop" / "period"  `.`
* "comma"  `,`
* "question mark"  `?`
* "undo"  `Ctrl+Z` (Optional advanced feature)



### 4.3. Feedback Systems

* **Visual:** A 20x20px semi-transparent red dot appears in the bottom-right corner when recording.
* *Critical:* This window must have the `topmost` and `transparent` flags set so clicks pass through it (it must not steal focus).


* **Audio:** (Optional) A subtle "click" sound on Activate/Deactivate.

---

## 5. Directory Structure & Code Organization

This structure ensures any developer can find the relevant code immediately.

```text
GhostType/
├── assets/                 # Icons, sound effects
├── models/                 # The Vosk model folder (e.g., vosk-model-small-en-us)
├── src/
│   ├── __init__.py
│   ├── main.py             # Entry point
│   ├── config.py           # Configuration loader (Singleton)
│   │
│   ├── core/               # Business Logic
│   │   ├── controller.py   # Orchestrates threads
│   │   ├── engine.py       # Wrapper for Vosk (Abstract Base Class)
│   │   ├── sanitizer.py    # Text formatting logic
│   │   └── injector.py     # Keyboard simulation logic
│   │
│   ├── services/           # I/O Services
│   │   ├── audio.py        # SoundDevice wrapper
│   │   └── input_hook.py   # Pynput global hotkey listener
│   │
│   └── ui/                 # Visuals
│       ├── tray.py         # System Tray Icon logic
│       └── overlay.py      # The "Red Dot" recording indicator
│
├── tests/                  # Unit tests
├── config.json             # User settings (Hotkeys, Model path)
├── requirements.txt        # Python dependencies
└── build_spec.spec         # PyInstaller configuration

```

---

## 6. Implementation Strategy (The "Maintainable" Way)

To make this **upgradable**, we use **Interfaces (Abstract Base Classes)**.

### 6.1. The Engine Interface

We define a generic contract for the speech engine. If you switch from Vosk to Whisper later, you only change the file `src/core/engine.py`. The rest of the app doesn't care.

```python
# src/core/interfaces.py
from abc import ABC, abstractmethod

class ISpeechEngine(ABC):
    @abstractmethod
    def start_stream(self):
        """Initialize resources"""
        pass

    @abstractmethod
    def process_audio(self, data: bytes) -> str:
        """Returns text string or None"""
        pass

```

### 6.2. Configuration Management

Do not hardcode hotkeys. Use `config.json` loaded at runtime.

```json
{
  "hotkey_ptt": "ctrl+alt",
  "hotkey_toggle": "ctrl+shift+v",
  "sound_feedback": true,
  "model_path": "./models/vosk-small"
}

```

---

## 7. Development Roadmap

### Phase 1: The "Skeleton" (MVP)

* **Goal:** Prove the pipeline works.
* **Tasks:**
1. Set up `AudioCapture` to read mic.
2. Set up `VoskEngine` to decode generic stream.
3. Connect `InputHook` to print text to console (no injection yet).



### Phase 2: The "Typer"

* **Goal:** Interact with the OS.
* **Tasks:**
1. Implement `Injector` (pynput keyboard controller).
2. Implement `Sanitizer` (Basic punctuation mapping).
3. Build the PyInstaller `.spec` to ensure the Model folder is bundled correctly inside the EXE.



### Phase 3: The "UX Polish"

* **Goal:** User Experience.
* **Tasks:**
1. Add `TrayIcon` (Quit, Settings).
2. Add `Overlay` (Visual feedback).
3. Optimize RAM (ensure Vosk unloads or pauses when not recording).



---

## 8. Specific Portability Constraints

Since this is a "Portable App":

1. **Path Handling:** Code must use `sys._MEIPASS` (PyInstaller temp path) to locate the Model and Assets at runtime, not relative paths.
2. **Permissions:** On Linux, the app must check if the user is in the `input` group. On Windows, it does not require Admin unless interacting with Admin windows (e.g., Task Manager).
3. **Cleanup:** On exit, the app must explicitly release the Microphone resource to prevent the OS from thinking the mic is still in use.