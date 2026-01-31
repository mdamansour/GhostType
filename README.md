# GhostType: Technical Specification & Architecture Document

**Version:** 1.0.0 (Complete Specification)
**Type:** Desktop Application (Portable / Background Service)
**License:** Open Source (MIT)
**Repository:** [https://github.com/mdamansour/GhostType](https://github.com/mdamansour/GhostType)
**Developer:** [Mohamed Amansour](https://www.linkedin.com/in/mdamansour/)

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

---

## 9. Error Handling & Recovery

### 9.1. Error Handling Matrix

| Error Scenario | Detection Method | Recovery Action | User Notification |
|---|---|---|---|
| **Microphone Disconnected** | `sounddevice.PortAudioError` | Stop recording, show tray notification | "Microphone disconnected. Recording stopped." |
| **Vosk Model Missing** | File check on startup | Show error dialog, exit gracefully | "Speech model not found. Please reinstall." |
| **Vosk Model Corrupted** | Exception during model load | Fallback to error state | "Speech model corrupted. Please reinstall." |
| **Audio Processing Failure** | Exception in worker thread | Log error, continue listening | Silent log (no user interruption) |
| **Keyboard Injection Failed** | `pynput` exception | Retry 3x, then skip text | "Cannot type into this window (elevated permissions)." |
| **Queue Overflow** | Queue size > 1000 items | Drop oldest items, log warning | Silent (performance degradation only) |
| **Worker Thread Crash** | Thread alive check every 5s | Restart worker thread | "Service restarted after error." |
| **Hotkey Conflict** | `pynput.keyboard.Listener` exception | Disable hotkey, notify user | "Hotkey conflict detected. Check config." |
| **Config File Invalid** | JSON parse error | Load defaults, backup corrupt file | "Config corrupted. Loaded defaults." |
| **Out of Memory** | `MemoryError` | Stop recording, clear queues | "Memory limit reached. Recording stopped." |

### 9.2. Graceful Degradation

- If overlay UI fails, continue without visual feedback
- If tray icon fails, continue in background (log to file for shutdown)
- If audio click fails, continue silently

### 9.3. Crash Recovery

- All crashes logged to `ghosttype_crash.log` in application directory
- Include: timestamp, Python traceback, system info (OS, Python version)
- Auto-send option (opt-in) for telemetry

---

## 10. Performance Requirements

### 10.1. Target Benchmarks

| Metric | Target | Measurement Method |
|---|---|---|
| **Latency (Speech → Text)** | < 500ms (P95) | Time from audio end to first keystroke |
| **RAM Usage (Idle)** | < 150 MB | Task Manager / `psutil` |
| **RAM Usage (Recording)** | < 250 MB | During 60s continuous dictation |
| **CPU Usage (Recording)** | < 25% (single core) | Average during 60s dictation |
| **Startup Time** | < 3 seconds | From .exe launch to tray icon ready |
| **Queue Processing Rate** | > 100 chunks/sec | Audio queue throughput |
| **.exe Size** | < 100 MB | PyInstaller output (with small model) |

### 10.2. Minimum System Requirements

- **OS:** Windows 10 (64-bit) or later, Ubuntu 20.04+ (X11), macOS 11+ (Intel/ARM)
- **CPU:** Dual-core 2.0 GHz or faster (SSE2 support)
- **RAM:** 4 GB (2 GB free)
- **Disk:** 200 MB free space
- **Audio:** Any USB/built-in microphone (16 kHz+ sample rate)

### 10.3. Constraints

- **Maximum Recording Duration:** 10 minutes continuous (auto-stop with warning)
- **Maximum Queue Size:** 1000 audio chunks (~30 seconds buffer)
- **Typing Speed:** 50-100 WPM simulation (configurable, prevents spam detection)

---

## 11. Platform Support

### 11.1. Windows

- **Supported Versions:** Windows 10 (1809+), Windows 11
- **Architecture:** x86-64 only (ARM via emulation, not optimized)
- **Keyboard Injection:** Uses `pynput` with Win32 API backend
- **UAC Limitation:** Cannot inject into elevated windows (Task Manager, installers)
- **Code Signing:** Required to avoid SmartScreen warnings (Phase 3)

### 11.2. Linux

- **Supported Distros:** Ubuntu 20.04+, Fedora 35+, Arch (latest)
- **Display Server:** X11 (primary), Wayland (limited - requires XWayland)
- **Permissions:** User must be in `input` group for global hotkeys
- **Audio Backend:** PulseAudio or PipeWire
- **Packaging:** AppImage (portable) + .deb (optional)

### 11.3. macOS

- **Supported Versions:** macOS 11 (Big Sur) and later
- **Architecture:** Intel (x86-64) and Apple Silicon (ARM64) universal binary
- **Permissions:** Requires Accessibility API approval (first-run prompt)
- **Notarization:** Required for Gatekeeper (Phase 3)
- **Audio:** CoreAudio via `sounddevice`

### 11.4. Cross-Platform Considerations

- Use `platform.system()` to detect OS and load platform-specific modules
- Abstract keyboard/audio backends in `services/` layer
- Test hotkey combinations per OS (e.g., `Cmd` vs `Ctrl`)

---

## 12. Vosk Model Management

### 12.1. Default Bundled Model

- **Model:** `vosk-model-small-en-us-0.15` (40 MB compressed)
- **Accuracy:** ~85% on clean speech, suitable for dictation
- **Languages:** English (US) only in MVP
- **Location:** Bundled inside PyInstaller .exe, extracted to temp on run

### 12.2. Model Validation

```python
# Pseudo-code for startup validation
def validate_model(model_path):
    required_files = ['am/final.mdl', 'graph/HCLR.fst', 'conf/model.conf']
    for file in required_files:
        if not os.path.exists(os.path.join(model_path, file)):
            raise ModelCorruptedError(f"Missing: {file}")
```

### 12.3. Multi-Language Support (Future)

- Phase 1: English only
- Phase 2: Add model downloader (German, French, Spanish)
- Config: `"language": "en-us"` → triggers model download if missing
- Model storage: `~/.ghosttype/models/` (outside .exe for swapping)

### 12.4. Custom Models

- Advanced users can replace model via config: `"model_path": "/custom/path"`
- Must conform to Vosk directory structure
- No validation for custom models (user responsibility)

---

## 13. Configuration Schema (Complete)

### 13.1. config.json (Full Specification)

```json
{
  "version": "1.0",
  
  "hotkeys": {
    "ptt": "ctrl+alt",
    "toggle": "ctrl+shift+v",
    "emergency_stop": "ctrl+alt+shift+s"
  },
  
  "audio": {
    "device": "default",
    "sample_rate": 16000,
    "channels": 1,
    "chunk_duration_ms": 100,
    "silence_threshold_db": -40,
    "silence_timeout_sec": 2.0
  },
  
  "speech": {
    "model_path": "auto",
    "language": "en-us",
    "enable_partial_results": false
  },
  
  "sanitizer": {
    "auto_capitalize": true,
    "auto_spacing": true,
    "keywords": {
      "new line": "\n",
      "period": ". ",
      "comma": ", ",
      "question mark": "? ",
      "exclamation mark": "! ",
      "colon": ": ",
      "semicolon": "; "
    }
  },
  
  "typing": {
    "speed_wpm": 80,
    "retry_on_failure": 3,
    "delay_between_keys_ms": 10
  },
  
  "ui": {
    "overlay_enabled": true,
    "overlay_position": "bottom-right",
    "overlay_color": "#FF0000",
    "overlay_opacity": 0.6,
    "sound_feedback": true,
    "tray_notifications": true
  },
  
  "system": {
    "max_recording_duration_sec": 600,
    "max_queue_size": 1000,
    "log_level": "INFO",
    "log_file": "ghosttype.log",
    "enable_crash_reports": false
  }
}
```

### 13.2. Validation Rules

| Parameter | Type | Valid Range | Default |
|---|---|---|---|
| `hotkeys.*` | String | Valid pynput key combo | See above |
| `audio.sample_rate` | Integer | 8000-48000 | 16000 |
| `audio.channels` | Integer | 1-2 | 1 |
| `sanitizer.auto_capitalize` | Boolean | true/false | true |
| `typing.speed_wpm` | Integer | 20-200 | 80 |
| `overlay_opacity` | Float | 0.1-1.0 | 0.6 |
| `max_recording_duration_sec` | Integer | 10-3600 | 600 |

### 13.3. Config Loading Priority

1. Command-line args (e.g., `--config=/path/to/config.json`)
2. `config.json` in .exe directory
3. `~/.ghosttype/config.json` (user profile)
4. Built-in defaults (hardcoded)

---

## 14. User Experience Flows

### 14.1. First-Run Experience

1. **Launch:** User double-clicks `GhostType.exe`
2. **Tray Icon Appears:** Small ghost icon in system tray with tooltip "GhostType Ready"
3. **Welcome Notification:** "Press Ctrl+Alt to start dictating" (auto-hide after 5s)
4. **Permission Check (macOS/Linux):** Prompt for Accessibility/Input permissions if needed
5. **Model Loading:** Progress indicator in tray tooltip ("Loading model... 50%")

### 14.2. Recording Flow (PTT Mode)

1. User presses `Ctrl+Alt` (default)
2. Red dot appears bottom-right
3. User speaks: "Hello world period new line"
4. User releases `Ctrl+Alt`
5. Red dot disappears
6. Text types out: "Hello world.\n" (with 10ms inter-key delay)

### 14.3. Recording Flow (Toggle Mode)

1. User double-presses `Ctrl+Shift+V` within 300ms
2. Red dot appears + tray icon changes to "Recording..."
3. User speaks for 2 minutes
4. User single-presses `Ctrl+Shift+V`
5. Recording stops, text injects

### 14.4. Settings Access

- Right-click tray icon → **Settings**
- Opens simple Tkinter dialog:
  - Hotkey configuration (with conflict detection)
  - Audio device dropdown (from `sounddevice.query_devices()`)
  - Model selection (if multiple installed)
  - Save button → validates and writes `config.json`

### 14.5. Error Notification Example

- **Scenario:** Microphone unplugged during recording
- **Action:** Red dot disappears, tray icon shows warning (⚠️)
- **Notification:** Balloon tip "Microphone disconnected"
- **Recovery:** User can replug and press hotkey again

---

## 15. Edge Cases & Race Conditions

### 15.1. Concurrency Issues

| Scenario | Behavior | Implementation |
|---|---|---|
| User presses PTT while Toggle active | Ignore PTT (Toggle takes priority) | State machine in `controller.py` |
| User double-presses Toggle rapidly | Debounce with 300ms window | Timestamp check |
| Multiple .exe instances launched | Second instance exits with message | PID file lock in temp directory |
| Rapid start/stop cycles | Queue drains before restart | `queue.join()` on stop |
| Audio chunk arrives after stop | Chunk discarded if timestamp old | Timestamped queue items |

### 15.2. Audio Edge Cases

- **Background Noise:** Vosk handles noise reasonably; no additional filtering
- **Silence Detection:** If 2s silence in Toggle mode, auto-finalize text (optional)
- **Very Long Recordings:** Auto-stop at 10 minutes, inject text so far, notify user
- **Whisper Speech:** May not detect; threshold configurable in `config.json`

### 15.3. Keyboard Injection Edge Cases

- **Fullscreen Games:** May block injection; not supported (by design)
- **Password Fields:** Injection works, but no special handling
- **Rich Text Editors:** Formatting lost (plain text only)
- **Command Prompts:** Works, but no command execution (safety)

---

## 16. Security & Privacy

### 16.1. Privacy Guarantees

- **Zero Network Activity:** No telemetry, no cloud, no analytics (unless crash reports enabled)
- **No Audio Storage:** Audio data deleted immediately after processing
- **No Transcript Logging:** Transcribed text never written to disk (except crash logs if error occurs)
- **Local-Only Processing:** All computation happens on user's machine

### 16.2. Logging Policy

- **Default Log Level:** `INFO` (no sensitive data)
- **What Gets Logged:**
  - Startup/shutdown events
  - Hotkey presses (not text content)
  - Errors and warnings
  - Performance metrics (latency, queue size)
- **What NEVER Gets Logged:**
  - Transcribed text content
  - Audio data
  - User's active window titles

### 16.3. Crash Reports (Opt-In)

- **Disabled by Default:** User must enable via `"enable_crash_reports": true`
- **Contents:** Stack trace, config (sanitized), system info
- **Destination:** Local file only (no auto-upload)

### 16.4. Code Signing

- **Windows:** Authenticode certificate (Phase 3 for release)
- **macOS:** Notarization with Apple Developer ID
- **Linux:** GPG-signed releases

---

## 17. Testing Strategy

### 17.1. Unit Tests

| Module | Coverage Target | Key Tests |
|---|---|---|
| `sanitizer.py` | 95% | Capitalization, keyword replacement, spacing |
| `config.py` | 90% | JSON parsing, validation, defaults |
| `engine.py` | 80% | Mock Vosk responses, error handling |
| `injector.py` | 70% | Mock keyboard (no real typing in tests) |

**Framework:** `pytest` with `pytest-cov`

### 17.2. Integration Tests

- **Audio → Vosk → Text:** Use pre-recorded WAV files (5 samples)
- **Hotkey → Controller:** Simulated key events
- **Queue Pipeline:** Producer/consumer stress test (1000 items)

### 17.3. Test Audio Samples

```
tests/audio/
  ├── clean_speech.wav      # "Hello world period"
  ├── noisy_speech.wav      # With background music
  ├── silent.wav            # 5 seconds silence
  ├── long_dictation.wav    # 2 minutes continuous
  └── multilingual.wav      # English + Spanish (fails gracefully)
```

### 17.4. Performance Testing

- **Benchmark Script:** `tests/benchmark.py`
  - Measures latency over 100 iterations
  - Records RAM usage via `psutil`
  - Outputs CSV for tracking over time

### 17.5. Manual Test Checklist

- [ ] Install on fresh Windows VM
- [ ] Test with 3 different microphones
- [ ] Verify works in: Notepad, Chrome, VSCode, Slack
- [ ] Test UAC-elevated window (should fail gracefully)
- [ ] Unplug mic during recording
- [ ] Fill disk to 0 MB free (should error cleanly)

---

## 18. Build & Distribution

### 18.1. PyInstaller Configuration

**File:** `build_spec.spec`

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('models/vosk-model-small-en-us-0.15', 'models/vosk-model-small-en-us-0.15'),
        ('assets/icon.ico', 'assets'),
        ('assets/click.wav', 'assets'),
        ('config.json', '.'),
    ],
    hiddenimports=['sounddevice', 'vosk', 'pynput', 'pystray'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy.testing'],  # Reduce size
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GhostType',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress (reduces size by ~30%)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
```

### 18.2. Build Commands

```bash
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build executable
pyinstaller build_spec.spec

# Output: dist/GhostType.exe (~85 MB)
```

### 18.3. Size Optimization

- Use `upx=True` (30% reduction)
- Exclude unused NumPy modules (`excludes` list)
- Use smallest Vosk model (40 MB vs 1.8 GB for large)
- Remove debug symbols (`strip=True` on Linux)

**Target:** < 100 MB final .exe

### 18.4. Release Artifacts

```
GhostType-v1.0.0-Windows.zip
  ├── GhostType.exe
  ├── README.txt           # Quick start guide
  ├── LICENSE.txt
  └── CHANGELOG.txt

GhostType-v1.0.0-Linux.AppImage
GhostType-v1.0.0-macOS.dmg
```

### 18.5. Versioning Strategy

- **Semantic Versioning:** MAJOR.MINOR.PATCH (e.g., 1.2.3)
- **MAJOR:** Breaking config changes, new languages
- **MINOR:** New features (Toggle mode, settings UI)
- **PATCH:** Bug fixes, performance improvements

### 18.6. Update Mechanism (Future)

- Phase 1: Manual download from GitHub Releases
- Phase 2: In-app "Check for Updates" (reads GitHub API)
- Phase 3: Auto-update with user confirmation

---

## 19. Dependencies (requirements.txt)

```text
# Core Speech Processing
vosk==0.3.45                # Offline speech recognition
sounddevice==0.4.6          # Audio capture

# System Integration
pynput==1.7.6               # Global hotkeys & keyboard injection
pystray==0.19.4             # System tray icon
Pillow==10.0.0              # Icon rendering for pystray

# GUI
# Tkinter is built-in to Python, no install needed

# Utilities
psutil==5.9.5               # System resource monitoring

# Build
pyinstaller==5.13.0         # Executable packaging

# Development/Testing
pytest==7.4.0
pytest-cov==4.1.0
pytest-mock==3.11.1
```

**Version Pinning:** All versions locked to prevent supply-chain attacks

---

## 20. Advanced Features Scope

### 20.1. MVP (Phase 1-2)

- ✅ PTT and Toggle modes
- ✅ Basic sanitizer (capitalization, punctuation keywords)
- ✅ Tray icon + overlay
- ✅ Single language (English)

### 20.2. v1.0 (Phase 3)

- 🔲 Settings UI (no manual JSON editing)
- 🔲 Microphone device selection
- 🔲 Custom keyword dictionary
- 🔲 Typing speed control
- 🔲 Code signing (Windows/macOS)

### 20.3. Future Versions

- 🔮 **Multi-language support** (v1.1)
- 🔮 **Undo command** (Ctrl+Z on voice, limited 10-action history) (v1.2)
- 🔮 **Text macros** ("my email" → expands to configured email) (v1.3)
- 🔮 **Command mode** ("open notepad" → executes system commands) (v2.0)
- 🔮 **Cloud model sync** (optional, for multi-device setups) (v2.0)

**Scope Discipline:** Features not in MVP are explicitly deferred to avoid scope creep.

---

## 21. Accessibility

### 21.1. Alternative Hotkeys

- **Single-Key Option:** F9 (for users unable to press Ctrl+Alt)
- **Configurable:** All hotkeys remappable via `config.json`

### 21.2. Visual Accessibility

- **High Contrast Overlay:** Option for white/yellow dot instead of red
- **Larger Overlay:** Configurable size (20px → 50px)
- **Screen Reader Compat:** Tray icon has proper ARIA labels (Windows Narrator)

### 21.3. Motor Impairment Support

- **Toggle Mode:** Designed for users who can't hold keys
- **Voice-Only Exit:** Say "stop listening" to exit Toggle mode (future)

---

## 22. Logging & Debugging

### 22.1. Log File Structure

**Location:** `ghosttype.log` (same directory as .exe)

**Format:**
```
2026-01-31 14:23:45 [INFO] GhostType v1.0.0 started
2026-01-31 14:23:46 [INFO] Loaded config from: config.json
2026-01-31 14:23:47 [INFO] Vosk model loaded: vosk-model-small-en-us-0.15
2026-01-31 14:23:47 [INFO] Audio device: Microphone (Realtek High Definition Audio)
2026-01-31 14:24:10 [INFO] Hotkey pressed: ptt
2026-01-31 14:24:12 [INFO] Transcribed 15 characters, latency: 420ms
2026-01-31 14:25:00 [ERROR] Keyboard injection failed: Access denied (UAC window)
2026-01-31 14:30:00 [INFO] GhostType shutting down
```

### 22.2. Log Rotation

- Max size: 10 MB
- When exceeded: Rename to `ghosttype.log.1`, start fresh `ghosttype.log`
- Keep last 3 rotations (30 MB total)

### 22.3. Debug Mode

**Activation:** `config.json` → `"log_level": "DEBUG"`

**Additional Output:**
- Audio chunk timestamps
- Queue sizes every second
- Thread states
- Vosk partial results (but still no transcribed text content)

### 22.4. Troubleshooting Guide

| Issue | Symptoms | Diagnosis | Solution |
|---|---|---|---|
| **No audio captured** | Red dot appears but no text | Check log for audio errors | Select correct mic in settings |
| **Hotkey doesn't work** | No response to key press | Check for conflicts (other apps) | Change hotkey in config.json |
| **Text types into wrong window** | Types into background app | Focus handling race condition | Add 100ms delay before typing |
| **High CPU usage** | Fan noise, sluggish | Vosk processing heavy audio | Use smaller model or reduce sample rate |
| **Crash on startup** | .exe exits immediately | Check `ghosttype_crash.log` | Reinstall, check model integrity |
| **Text appears garbled** | Wrong characters | Keyboard layout mismatch | Ensure system locale is English (for MVP) |

---

## 23. Resource Cleanup & Shutdown

### 23.1. Shutdown Sequence

1. **User triggers exit** (Tray → Quit or Ctrl+C in debug mode)
2. **Stop accepting new recordings** (Hotkeys disabled)
3. **Signal worker threads to stop** (Event flags set)
4. **Drain queues** (Process remaining items, max 5s timeout)
5. **Release microphone** (`audio_stream.stop()`, `audio_stream.close()`)
6. **Unload Vosk model** (`del recognizer`, force garbage collection)
7. **Save any pending config changes**
8. **Write final log entry** ("Shutdown complete")
9. **Exit process** (`sys.exit(0)`)

### 23.2. Forced Shutdown

- If graceful shutdown takes > 10 seconds, force kill
- Log warning: "Forced shutdown after timeout"

### 23.3. Cleanup on Crash

- Python's `atexit` module registers cleanup handlers
- Ensures mic release even on unhandled exceptions
- Temp files (PyInstaller extraction) auto-deleted by OS on process end

---

## 24. Known Limitations

1. **UAC/Elevated Windows:** Cannot inject text (Windows security by design)
2. **Accuracy:** 85% on Vosk small model (vs 95%+ for cloud services)
3. **Languages:** English-only in MVP (extensible later)
4. **Rich Text:** Formatting not preserved (plain text only)
5. **Punctuation:** Requires voice commands ("period", "comma"), not automatic
6. **Wayland:** Limited support on Linux (requires XWayland)
7. **Gaming:** May not work in fullscreen exclusive mode

---

## 25. Success Metrics

### 25.1. Technical KPIs

- **Crash Rate:** < 1% of sessions
- **Latency P95:** < 500ms
- **Model Load Time:** < 2 seconds
- **Memory Leak:** 0 MB growth over 1 hour

### 25.2. User Experience KPIs

- **Setup Time:** < 1 minute (download, unzip, double-click)
- **First Dictation Success:** > 90% of users succeed on first try
- **Accuracy Satisfaction:** > 75% of users rate "good enough"

---

## 26. Future Vision

**GhostType 2.0 (2027):**
- Multi-language support (10+ languages)
- Cloud-synced custom dictionaries
- Voice commands for OS control ("open browser", "switch window")
- Mobile companion app (dictate on phone, types on PC)

**GhostType Enterprise (2028):**
- Medical/legal vocabulary models
- Shared team dictionaries
- Compliance logging (HIPAA, etc.)

---

## 27. Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, and PR guidelines.

**Quick Start for Contributors:**
```bash
git clone https://github.com/mdamansour/GhostType.git
cd GhostType
pip install -r requirements.txt
python src/main.py  # Run from source
pytest tests/       # Run tests
```

---

## 28. License

MIT License - See [LICENSE](LICENSE) for details.

---

**Document Status:** ✅ Complete Specification (Ready for Development)
**Last Updated:** January 31, 2026
**Maintained By:** [Mohamed Amansour](https://www.linkedin.com/in/mdamansour/)