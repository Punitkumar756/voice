# 🤖 AI Voice Assistant

A powerful, feature-rich voice-controlled assistant for Windows with a beautiful web interface. Control your PC, manage applications, and execute commands using your voice or text input.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🎯 Core Capabilities
- **Voice Recognition** - Advanced speech-to-text using Google Speech Recognition
- **Text-to-Speech** - Natural voice responses using pyttsx3
- **Web Interface** - Beautiful, modern UI with animations and real-time feedback
- **Universal App Control** - Open, close, and switch between ANY application on your PC
- **System Management** - Full control over system operations

### 🚀 What It Can Do

#### 📱 Application Control
- Open any installed application by name
- Close running applications
- List all open windows
- Switch between applications
- Dynamic system-wide app search

#### ⌨️ Universal Keyboard Shortcuts
- Copy, Paste, Cut, Undo, Redo
- Save, Select All, Find, Print
- New Tab, Close Tab, Refresh
- Works across ALL applications

#### 🔧 System Operations
- Volume control (up, down, mute)
- Take screenshots
- Shutdown, restart, sleep/hibernate
- Lock computer
- Open Task Manager, Settings, Control Panel
- Window management (minimize, maximize)

#### 🌐 Web & Search
- Google search
- Open popular websites (YouTube, Gmail, Facebook, etc.)
- Wikipedia search

#### 📝 File & Notes
- Create files and folders
- Take voice notes
- Automatic file management

#### 🎮 Entertainment & Info
- Tell jokes
- Get current time and date
- Battery status
- CPU usage monitoring
- Play music from your Music folder

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- Windows OS (for system-specific features)
- Working microphone
- Internet connection (for voice recognition)

### Step 1: Clone or Download
```bash
git clone https://github.com/yourusername/voice-assistant.git
cd voice-assistant
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install SpeechRecognition pyttsx3 PyAudio wikipedia-api pyautogui requests psutil Flask
```

### Step 3: Run the Assistant

**Option 1: Web Interface (Recommended)**
```bash
python app.py
```
Then open your browser to: `http://localhost:5000`

**Option 2: Command Line**
```bash
python voice.py
```

## 🎨 Web Interface

The web interface features:
- 🎭 Modern gradient design with animated background
- 🎤 Interactive microphone avatar with sound waves
- ⚡ Real-time status indicators
- 📱 Responsive design for all screen sizes
- 🔘 Quick action buttons for common commands
- ✍️ Text input alternative to voice commands

## 📖 Usage Guide

### Voice Commands

#### Greetings & Basic Info
```
"Hello" / "Hi"
"What's the time?"
"What's the date?"
"Who are you?"
```

#### Opening Applications
```
"Open [app name]"
Examples:
- "Open calculator"
- "Open Chrome"
- "Open Notepad"
- "Open Photoshop"
- "Open VS Code"
```

#### Closing Applications
```
"Close [app name]"
"Close window" (closes current window)
Examples:
- "Close Chrome"
- "Close Notepad"
```

#### Window Management
```
"List windows"
"Show windows"
"Switch to [app name]"
"Switch application"
"Minimize window"
"Maximize window"
```

#### Keyboard Shortcuts
```
"Copy"
"Paste"
"Cut"
"Undo"
"Redo"
"Save"
"Select all"
"Find"
"Print"
"New tab"
"Close tab"
"Refresh"
```

#### Volume Control
```
"Volume up"
"Volume down"
"Mute"
```

#### System Operations
```
"Take screenshot"
"Shutdown"
"Restart"
"Sleep"
"Lock computer"
"Task manager"
"Open settings"
```

#### Web & Search
```
"Search for [query]"
"Google [query]"
"Open YouTube"
"Open Gmail"
"Open Facebook"
"Wikipedia" (then speak topic)
```

#### Files & Notes
```
"Create file"
"Create folder"
"Take note" / "Write note"
```

#### Entertainment
```
"Tell me a joke"
"Play music"
```

#### System Info
```
"Battery" (laptop only)
"CPU"
```

#### Exit
```
"Exit"
"Quit"
"Goodbye"
```

## 🗂️ Project Structure

```
voice-assistant/
│
├── app.py                 # Flask web application
├── voice.py              # Command-line voice assistant
├── requirements.txt      # Python dependencies
├── README.md            # This file
│
├── templates/
│   └── index.html       # Web interface HTML
│
└── static/
    ├── style.css        # Beautiful CSS styling
    └── script.js        # Frontend JavaScript
```

## 🛠️ Configuration

### Changing Voice Settings
Edit the TTS engine properties in `voice.py` or `app.py`:

```python
self.engine.setProperty('rate', 180)  # Speech speed
self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
```

### Changing Voice Gender
```python
voices = self.engine.getProperty('voices')
self.engine.setProperty('voice', voices[0].id)  # Male
# or
self.engine.setProperty('voice', voices[1].id)  # Female
```

### Customizing Port
In `app.py`, change the port number:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change 5000 to your port
```

## 🔧 Troubleshooting

### Microphone Not Working
1. Check if your microphone is properly connected
2. Ensure microphone permissions are enabled for Python
3. Run the calibration again by restarting the application

### PyAudio Installation Issues
On Windows, if PyAudio fails to install:
```bash
pip install pipwin
pipwin install pyaudio
```

### Application Not Found
The assistant searches common installation directories. If an app isn't found:
- Make sure it's installed
- Try using the full application name
- Check if the .exe is in your PATH

### Web Interface Not Loading
1. Ensure Flask is installed: `pip install Flask`
2. Check if port 5000 is available
3. Try accessing `http://127.0.0.1:5000` instead

## 🚀 Advanced Features

### Adding Custom Applications
Edit the `quick_apps` dictionary in `handle_open_application()`:

```python
quick_apps = {
    "your_app": "path/to/your_app.exe",
}
```

### Adding Custom Commands
Add new conditions in the `process_command()` method:

```python
elif "your command" in command:
    # Your custom action
    self.speak("Response message")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Speech Recognition API for voice recognition
- pyttsx3 for text-to-speech
- Flask for the web framework
- Font Awesome for icons
- All open-source contributors

## 📧 Contact

Punit Kumar - Punitkumarmorawal2003@gmail.com



## 🔮 Future Enhancements

- [ ] Multiple language support
- [ ] Custom wake word detection
- [ ] Integration with smart home devices
- [ ] Calendar and reminder management
- [ ] Email sending capabilities
- [ ] Weather API integration
- [ ] News API integration
- [ ] Spotify/Music streaming control
- [ ] AI conversation capabilities
- [ ] Mobile app version

## ⚠️ Disclaimer

This assistant requires microphone access and system permissions. Use responsibly and ensure you trust the code before granting such permissions.

---

Made with ❤️ by Punit Kumar

⭐ Star this repo if you find it helpful!
