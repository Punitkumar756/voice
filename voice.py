import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipediaapi
import time
import sys
import os
import subprocess
import pyautogui
import requests
import json
from pathlib import Path
import re
import psutil
import ctypes

class VoiceAssistant:
    """
    A simple voice assistant class for Python.
    """
    
    def __init__(self):
        """
        Initializes the TTS engine, recognizer, and Wikipedia API.
        """
        print("Initializing assistant...")
        
        # --- Text-to-Speech (TTS) Setup ---
        try:
            self.engine = pyttsx3.init()
            # Optional: Adjust voice properties
            voices = self.engine.getProperty('voices')
            # You can change the index to try different voices
            # self.engine.setProperty('voice', voices[1].id) 
            self.engine.setProperty('rate', 180) # Speed of speech
        except Exception as e:
            print(f"Error initializing TTS engine: {e}")
            print("Please ensure you have a compatible TTS engine installed (e.g., eSpeak, SAPI5 on Windows, NSSpeechSynthesizer on macOS)")
            sys.exit(1)

        # --- Speech Recognition Setup ---
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise once at the start
        try:
            with self.microphone as source:
                print("Calibrating microphone... Please wait a moment.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print("Microphone calibrated.")
        except Exception as e:
            print(f"Could not access microphone: {e}")
            self.speak("Error: Could not access the microphone. Please check your system settings.")
            sys.exit(1)

        # --- Wikipedia API Setup ---
        # Using 'wikipedia-api' for easier language handling and summaries
        self.wiki_api = wikipediaapi.Wikipedia(
            user_agent='VoiceAssistant/1.0',
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )

    def speak(self, text):
        """
        Converts text to speech.
        """
        print(f"Assistant: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error during speech: {e}")

    def greet_user(self):
        """
        Greets the user based on the time of day.
        """
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            greeting = "Good morning!"
        elif 12 <= hour < 18:
            greeting = "Good afternoon!"
        else:
            greeting = "Good evening!"
        
        self.speak(f"{greeting} I am Chanakya, your voice assistant. How can I assist you today?")

    def listen_for_command(self):
        """
        Listens for a command from the user and returns it as text.
        """
        command = None
        try:
            with self.microphone as source:
                print("\nListening...")
                # Timeout: max seconds it will wait for a phrase to start
                # Phrase time limit: max seconds it will listen for a phrase
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            print("Recognizing...")
            # Use Google's Web Speech API for recognition
            command = self.recognizer.recognize_google(audio)
            command = command.lower()
            print(f"User said: {command}")

        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start.")
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            # self.speak("Sorry, I didn't catch that. Could you please repeat?")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            self.speak("Sorry, my speech service is down. Please check your internet connection.")
        except Exception as e:
            print(f"An unexpected error occurred during listening: {e}")

        return command

    def process_command(self, command):
        """
        Analyzes the command and performs the appropriate action.
        Returns True if the assistant should continue running, False if it should stop.
        """
        if command is None:
            return True # Continue running

        # --- Core Commands ---
        if "hello" in command or "hi" in command:
            self.speak("Hello! It's nice to hear from you.")
        
        elif "what's the time" in command or "what time is it" in command:
            now = datetime.datetime.now().strftime("%I:%M %p") # e.g., "02:30 PM"
            self.speak(f"The current time is {now}.")
        
        # --- Wikipedia Search ---
        elif "wikipedia" in command:
            self.handle_wikipedia_search(command)
        
        # --- Web Search ---
        elif "search for" in command:
            self.handle_web_search(command, "search for")
        elif "google" in command:
            self.handle_web_search(command, "google")

        # --- Open Applications ---
        elif "open" in command:
            self.handle_open_application(command)
        
        # --- Close Applications ---
        elif "close" in command:
            self.handle_close_application(command)
        
        # --- Window Management ---
        elif "list windows" in command or "show windows" in command or "open windows" in command:
            self.list_open_windows()
        elif "switch to" in command or "switch window" in command:
            self.switch_window(command)
        elif "minimize window" in command or "minimize" in command:
            self.speak("Minimizing current window.")
            pyautogui.hotkey('win', 'down')
        elif "maximize window" in command or "maximize" in command:
            self.speak("Maximizing current window.")
            pyautogui.hotkey('win', 'up')
        
        # --- Universal Keyboard Shortcuts ---
        elif "copy" in command and "paste" not in command:
            pyautogui.hotkey('ctrl', 'c')
            self.speak("Copied.")
        elif "paste" in command:
            pyautogui.hotkey('ctrl', 'v')
            self.speak("Pasted.")
        elif "cut" in command:
            pyautogui.hotkey('ctrl', 'x')
            self.speak("Cut.")
        elif "undo" in command:
            pyautogui.hotkey('ctrl', 'z')
            self.speak("Undone.")
        elif "redo" in command:
            pyautogui.hotkey('ctrl', 'y')
            self.speak("Redone.")
        elif "save" in command and "screenshot" not in command:
            pyautogui.hotkey('ctrl', 's')
            self.speak("Saved.")
        elif "select all" in command:
            pyautogui.hotkey('ctrl', 'a')
            self.speak("Selected all.")
        elif "find" in command or "search" in command and "google" not in command and "for" not in command:
            pyautogui.hotkey('ctrl', 'f')
            self.speak("Opening find dialog.")
        elif "print" in command:
            pyautogui.hotkey('ctrl', 'p')
            self.speak("Opening print dialog.")
        elif "new tab" in command:
            pyautogui.hotkey('ctrl', 't')
            self.speak("Opening new tab.")
        elif "close tab" in command:
            pyautogui.hotkey('ctrl', 'w')
            self.speak("Closing tab.")
        elif "refresh" in command or "reload" in command:
            pyautogui.hotkey('ctrl', 'r')
            self.speak("Refreshing.")
        
        # --- Task Manager ---
        elif "task manager" in command or "open task manager" in command:
            pyautogui.hotkey('ctrl', 'shift', 'esc')
            self.speak("Opening task manager.")
        
        # --- Lock Computer ---
        elif "lock" in command and "computer" in command:
            self.speak("Locking computer.")
            ctypes.windll.user32.LockWorkStation()
        
        # --- Alt+Tab ---
        elif "switch application" in command or "next window" in command:
            pyautogui.hotkey('alt', 'tab')
            self.speak("Switching application.")
        
        # --- Volume Control ---
        elif "volume up" in command or "increase volume" in command:
            self.adjust_volume("up")
        elif "volume down" in command or "decrease volume" in command:
            self.adjust_volume("down")
        elif "mute" in command:
            self.adjust_volume("mute")
        
        # --- System Operations ---
        elif "shutdown" in command:
            self.speak("Shutting down the system in 10 seconds. Say cancel to stop.")
            time.sleep(5)
            os.system("shutdown /s /t 10")
        elif "restart" in command:
            self.speak("Restarting the system in 10 seconds.")
            time.sleep(5)
            os.system("shutdown /r /t 10")
        elif "sleep" in command or "hibernate" in command:
            self.speak("Putting the system to sleep.")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        
        # --- Screen Control ---
        elif "screenshot" in command or "take screenshot" in command:
            self.take_screenshot()
        
        # --- File Operations ---
        elif "create file" in command or "make file" in command:
            self.handle_create_file()
        elif "create folder" in command or "make folder" in command:
            self.handle_create_folder()
        
        # --- Notes ---
        elif "take note" in command or "write note" in command or "remember this" in command:
            self.take_note()
        
        # --- Weather ---
        elif "weather" in command:
            self.get_weather()
        
        # --- Calculator ---
        elif "calculate" in command or "what is" in command and any(op in command for op in ["+", "-", "*", "/", "plus", "minus", "times", "divided"]):
            self.calculate(command)
        
        # --- Date ---
        elif "what's the date" in command or "what date is it" in command or "today's date" in command:
            now = datetime.datetime.now().strftime("%B %d, %Y") # e.g., "December 24, 2025"
            self.speak(f"Today is {now}.")
        
        # --- Play Music ---
        elif "play music" in command or "play song" in command:
            self.play_music(command)
        
        # --- Tell Joke ---
        elif "tell joke" in command or "tell me a joke" in command:
            self.tell_joke()
        
        # --- News ---
        elif "news" in command or "headlines" in command:
            self.get_news()
        
        # --- System Information ---
        elif "battery" in command:
            self.get_battery_status()
        elif "cpu" in command or "processor" in command:
            self.get_cpu_info()
        
        # --- Open Websites ---
        elif "open youtube" in command:
            self.speak("Opening YouTube.")
            webbrowser.open("https://www.youtube.com")
        elif "open gmail" in command or "open email" in command:
            self.speak("Opening Gmail.")
            webbrowser.open("https://mail.google.com")
        elif "open facebook" in command:
            self.speak("Opening Facebook.")
            webbrowser.open("https://www.facebook.com")
        elif "open twitter" in command:
            self.speak("Opening Twitter.")
            webbrowser.open("https://www.twitter.com")
        elif "open instagram" in command:
            self.speak("Opening Instagram.")
            webbrowser.open("https://www.instagram.com")
        
        # --- Who are you ---
        elif "who are you" in command or "what is your name" in command:
            self.speak("I am Chanakya, your personal voice assistant. I'm here to help you with various tasks and control your PC.")
        
        # --- Exit Command ---
        elif "exit" in command or "quit" in command or "stop" in command or "goodbye" in command:
            self.speak("Goodbye! Have a great day.")
            return False # Signal to stop
            
        else:
            # Fallback for unhandled commands
            self.speak("I'm not sure how to help with that. Can you try rephrasing?")

        return True # Signal to continue

    def handle_wikipedia_search(self, command):
        """
        Handles Wikipedia search logic.
        """
        try:
            self.speak("What topic would you like to search for on Wikipedia?")
            query = self.listen_for_command()
            
            if query:
                self.speak(f"Searching Wikipedia for {query}...")
                page = self.wiki_api.page(query)
                
                if not page.exists():
                    self.speak(f"Sorry, I couldn't find a Wikipedia page for {query}.")
                else:
                    # Get the first paragraph of the summary
                    summary = page.summary.split('\n')[0]
                    self.speak("According to Wikipedia:")
                    self.speak(summary)
            else:
                self.speak("I didn't hear a search query.")
        except Exception as e:
            print(f"Error during Wikipedia search: {e}")
            self.speak("Sorry, I ran into an error while searching Wikipedia.")

    def handle_web_search(self, command, keyword):
        """
        Handles web search logic.
        """
        try:
            # Find the index of the keyword and take everything after it
            query_index = command.find(keyword) + len(keyword)
            query = command[query_index:].strip()
            
            if not query:
                self.speak(f"What would you like me to {keyword}?")
                query = self.listen_for_command()
            
            if query:
                url = f"https://www.google.com/search?q={query}"
                self.speak(f"Opening Google search for {query} in your browser.")
                webbrowser.open(url)
            else:
                self.speak("I didn't hear a search query.")
        except Exception as e:
            print(f"Error opening browser: {e}")
            self.speak("Sorry, I couldn't open your web browser.")

    def handle_open_application(self, command):
        """
        Opens applications based on voice command - now searches entire system.
        """
        try:
            # Extract app name from command
            app_name = command.replace("open", "").strip()
            
            # First try common quick apps
            quick_apps = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "chrome": "chrome.exe",
                "edge": "msedge.exe",
                "firefox": "firefox.exe",
                "explorer": "explorer.exe",
                "file explorer": "explorer.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
                "powerpoint": "powerpnt.exe",
                "vs code": "code",
                "visual studio code": "code",
                "spotify": "spotify.exe",
                "discord": "discord.exe",
                "steam": "steam.exe",
                "cmd": "cmd.exe",
                "command prompt": "cmd.exe",
                "powershell": "powershell.exe",
                "control panel": "control.exe",
                "settings": "ms-settings:"
            }
            
            # Check quick apps first
            for app_key, app_exe in quick_apps.items():
                if app_key in app_name.lower():
                    self.speak(f"Opening {app_key}.")
                    try:
                        if app_exe == "ms-settings:":
                            os.system("start ms-settings:")
                        else:
                            subprocess.Popen(app_exe, shell=True)
                        return
                    except Exception as e:
                        print(f"Error opening {app_key}: {e}")
            
            # If not found in quick apps, search system
            self.speak(f"Searching for {app_name}.")
            found_app = self.find_application(app_name)
            
            if found_app:
                self.speak(f"Opening {app_name}.")
                try:
                    subprocess.Popen(found_app, shell=True)
                except Exception as e:
                    print(f"Error opening {found_app}: {e}")
                    self.speak(f"Found {app_name} but couldn't open it.")
            else:
                self.speak(f"Sorry, I couldn't find {app_name} on your system.")
                
        except Exception as e:
            print(f"Error in handle_open_application: {e}")
            self.speak("Sorry, I encountered an error while trying to open the application.")
    
    def find_application(self, app_name):
        """
        Searches the system for an application by name.
        """
        try:
            # Common installation directories
            search_paths = [
                Path(os.environ.get('ProgramFiles', 'C:\\Program Files')),
                Path(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')),
                Path(os.environ.get('LOCALAPPDATA', '')),
                Path(os.environ.get('APPDATA', '')),
                Path.home() / 'AppData' / 'Local' / 'Programs',
            ]
            
            # Search for .exe files matching the app name
            for search_path in search_paths:
                if not search_path.exists():
                    continue
                    
                # Search up to 3 levels deep
                for depth in range(3):
                    pattern = '*/' * depth + '*.exe'
                    for exe_file in search_path.glob(pattern):
                        exe_name = exe_file.stem.lower()
                        if app_name.lower() in exe_name or exe_name in app_name.lower():
                            return str(exe_file)
            
            return None
        except Exception as e:
            print(f"Error searching for application: {e}")
            return None
    
    def handle_close_application(self, command):
        """
        Closes an application by name.
        """
        try:
            app_name = command.replace("close", "").strip()
            
            if not app_name or app_name == "window":
                # Close current window
                pyautogui.hotkey('alt', 'f4')
                self.speak("Closing current window.")
                return
            
            # Find and close process
            closed = False
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if app_name.lower() in proc_name:
                        proc.terminate()
                        self.speak(f"Closed {app_name}.")
                        closed = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if not closed:
                self.speak(f"Couldn't find {app_name} running.")
                
        except Exception as e:
            print(f"Error closing application: {e}")
            self.speak("Sorry, I couldn't close that application.")
    
    def list_open_windows(self):
        """
        Lists all open windows/applications.
        """
        try:
            windows = []
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name']
                    if proc_name.endswith('.exe') and proc_name not in windows:
                        windows.append(proc_name.replace('.exe', ''))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if windows:
                # Get first 5 most relevant apps (exclude system processes)
                filtered = [w for w in windows if w.lower() not in ['svchost', 'system', 'registry', 'csrss', 'winlogon', 'services']]
                top_windows = filtered[:5]
                
                self.speak(f"Open applications: {', '.join(top_windows)}")
            else:
                self.speak("No applications currently running.")
                
        except Exception as e:
            print(f"Error listing windows: {e}")
            self.speak("Sorry, I couldn't list the windows.")
    
    def switch_window(self, command):
        """
        Switches to a specific window by name.
        """
        try:
            app_name = command.replace("switch to", "").replace("switch window", "").strip()
            
            if not app_name:
                # Just alt+tab if no specific app mentioned
                pyautogui.hotkey('alt', 'tab')
                self.speak("Switching window.")
                return
            
            # Try to bring window to front
            found = False
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    proc_name = proc.info['name'].lower()
                    if app_name.lower() in proc_name:
                        # Use alt+tab multiple times to cycle through windows
                        pyautogui.hotkey('alt', 'tab')
                        time.sleep(0.2)
                        self.speak(f"Switching to {app_name}.")
                        found = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if not found:
                self.speak(f"Couldn't find {app_name} running.")
                
        except Exception as e:
            print(f"Error switching window: {e}")
            self.speak("Sorry, I couldn't switch windows.")

    def adjust_volume(self, action):
        """
        Adjusts system volume.
        """
        try:
            if action == "up":
                for _ in range(5):
                    pyautogui.press("volumeup")
                self.speak("Volume increased.")
            elif action == "down":
                for _ in range(5):
                    pyautogui.press("volumedown")
                self.speak("Volume decreased.")
            elif action == "mute":
                pyautogui.press("volumemute")
                self.speak("Volume muted.")
        except Exception as e:
            print(f"Error adjusting volume: {e}")
            self.speak("Sorry, I couldn't adjust the volume.")

    def take_screenshot(self):
        """
        Takes a screenshot and saves it.
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            desktop = Path.home() / "Desktop"
            screenshot_path = desktop / f"screenshot_{timestamp}.png"
            
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            self.speak(f"Screenshot saved to desktop as screenshot_{timestamp}.png")
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            self.speak("Sorry, I couldn't take a screenshot.")

    def handle_create_file(self):
        """
        Creates a new file.
        """
        try:
            self.speak("What should I name the file?")
            filename = self.listen_for_command()
            
            if filename:
                desktop = Path.home() / "Desktop"
                filepath = desktop / f"{filename}.txt"
                
                self.speak("What content should I add to the file?")
                content = self.listen_for_command()
                
                with open(filepath, 'w') as f:
                    f.write(content if content else "")
                
                self.speak(f"File {filename}.txt created on desktop.")
            else:
                self.speak("I didn't hear a filename.")
        except Exception as e:
            print(f"Error creating file: {e}")
            self.speak("Sorry, I couldn't create the file.")

    def handle_create_folder(self):
        """
        Creates a new folder.
        """
        try:
            self.speak("What should I name the folder?")
            foldername = self.listen_for_command()
            
            if foldername:
                desktop = Path.home() / "Desktop"
                folderpath = desktop / foldername
                folderpath.mkdir(exist_ok=True)
                
                self.speak(f"Folder {foldername} created on desktop.")
            else:
                self.speak("I didn't hear a folder name.")
        except Exception as e:
            print(f"Error creating folder: {e}")
            self.speak("Sorry, I couldn't create the folder.")

    def take_note(self):
        """
        Takes notes and saves them to a file.
        """
        try:
            self.speak("What should I write?")
            note = self.listen_for_command()
            
            if note:
                desktop = Path.home() / "Desktop"
                notes_file = desktop / "voice_notes.txt"
                
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(notes_file, 'a') as f:
                    f.write(f"\n[{timestamp}] {note}\n")
                
                self.speak("Note saved successfully.")
            else:
                self.speak("I didn't hear anything to note.")
        except Exception as e:
            print(f"Error taking note: {e}")
            self.speak("Sorry, I couldn't save the note.")

    def get_weather(self):
        """
        Gets weather information (requires API key).
        """
        self.speak("Weather feature requires an API key. Please set up OpenWeatherMap API.")
        # To implement: Get API key from OpenWeatherMap and add city detection
        # api_key = "YOUR_API_KEY"
        # city = "YOUR_CITY"
        # url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        # response = requests.get(url)
        # weather_data = response.json()

    def calculate(self, command):
        """
        Performs basic calculations.
        """
        try:
            # Extract the mathematical expression
            command = command.replace("calculate", "").replace("what is", "").strip()
            command = command.replace("plus", "+").replace("minus", "-")
            command = command.replace("times", "*").replace("multiplied by", "*")
            command = command.replace("divided by", "/").replace("divide", "/")
            
            # Remove non-mathematical characters
            allowed_chars = "0123456789+-*/.()"
            expression = ''.join(c for c in command if c in allowed_chars or c.isspace())
            expression = expression.replace(" ", "")
            
            if expression:
                result = eval(expression)
                self.speak(f"The result is {result}")
            else:
                self.speak("I couldn't understand the calculation.")
        except Exception as e:
            print(f"Error calculating: {e}")
            self.speak("Sorry, I couldn't perform that calculation.")

    def play_music(self, command):
        """
        Plays music from a default music directory.
        """
        try:
            music_dir = Path.home() / "Music"
            if music_dir.exists():
                songs = list(music_dir.glob("*.mp3"))
                if songs:
                    song = str(songs[0])
                    os.startfile(song)
                    self.speak("Playing music.")
                else:
                    self.speak("No music files found in the Music folder.")
            else:
                self.speak("Music folder not found. You can also say 'open YouTube' for music.")
        except Exception as e:
            print(f"Error playing music: {e}")
            self.speak("Sorry, I couldn't play music.")

    def tell_joke(self):
        """
        Tells a random joke.
        """
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't programmers like nature? It has too many bugs!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why did the math book look so sad? Because it had too many problems!"
        ]
        import random
        joke = random.choice(jokes)
        self.speak(joke)

    def get_news(self):
        """
        Gets latest news headlines (requires API key).
        """
        self.speak("News feature requires an API key. Please set up NewsAPI.")
        # To implement: Get API key from NewsAPI
        # api_key = "YOUR_API_KEY"
        # url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
        # response = requests.get(url)
        # news_data = response.json()

    def get_battery_status(self):
        """
        Gets battery status.
        """
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                plugged = "plugged in" if battery.power_plugged else "not plugged in"
                self.speak(f"Battery is at {percent} percent and {plugged}.")
            else:
                self.speak("Battery information not available. You might be on a desktop.")
        except ImportError:
            self.speak("Battery monitoring requires the psutil library. Install it with: pip install psutil")
        except Exception as e:
            print(f"Error getting battery status: {e}")
            self.speak("Sorry, I couldn't check the battery status.")

    def get_cpu_info(self):
        """
        Gets CPU usage information.
        """
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            self.speak(f"CPU usage is at {cpu_percent} percent.")
        except ImportError:
            self.speak("CPU monitoring requires the psutil library. Install it with: pip install psutil")
        except Exception as e:
            print(f"Error getting CPU info: {e}")
            self.speak("Sorry, I couldn't check the CPU usage.")

    def run(self):
        """
        Main loop for the assistant.
        """
        self.greet_user()
        running = True
        while running:
            command = self.listen_for_command()
            running = self.process_command(command)

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()
