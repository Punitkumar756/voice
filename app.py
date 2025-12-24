from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipediaapi
import time
import os
import subprocess
import pyautogui
import requests
import json
from pathlib import Path
import re
import psutil
import ctypes
import threading

app = Flask(__name__)

class VoiceAssistantWeb:
    def __init__(self):
        print("Initializing web assistant...")
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        
        # Calibrate microphone
        try:
            with self.microphone as source:
                print("Calibrating microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print("Microphone calibrated.")
        except Exception as e:
            print(f"Could not access microphone: {e}")
        
        self.wiki_api = wikipediaapi.Wikipedia(
            user_agent='VoiceAssistant/1.0',
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )

    def speak(self, text):
        print(f"Assistant: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error during speech: {e}")

    def listen_for_command(self):
        command = None
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            print("Recognizing...")
            command = self.recognizer.recognize_google(audio)
            command = command.lower()
            print(f"User said: {command}")
        except sr.WaitTimeoutError:
            print("Listening timed out.")
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
        except sr.RequestError as e:
            print(f"Could not request results: {e}")
        except Exception as e:
            print(f"Error: {e}")
        
        return command

    def process_command(self, command):
        if command is None:
            return {"status": "no_command", "response": "I didn't hear anything."}
        
        response = ""
        action = ""
        
        # Core Commands
        if "hello" in command or "hi" in command:
            response = "Hello! I'm Chanakya. It's nice to hear from you."
            action = "greeting"
        
        elif "time" in command:
            now = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The current time is {now}."
            action = "time"
        
        elif "date" in command:
            now = datetime.datetime.now().strftime("%B %d, %Y")
            response = f"Today is {now}."
            action = "date"
        
        elif "open" in command and "windows" not in command:
            app_name = command.replace("open", "").strip()
            self.open_application(app_name)
            response = f"Opening {app_name}."
            action = "open_app"
        
        elif "close" in command:
            app_name = command.replace("close", "").strip()
            self.close_application(app_name)
            response = f"Closing {app_name}."
            action = "close_app"
        
        elif "list windows" in command:
            windows = self.list_windows()
            response = f"Open applications: {', '.join(windows[:5])}"
            action = "list_windows"
        
        elif "volume up" in command:
            for _ in range(5):
                pyautogui.press("volumeup")
            response = "Volume increased."
            action = "volume_up"
        
        elif "volume down" in command:
            for _ in range(5):
                pyautogui.press("volumedown")
            response = "Volume decreased."
            action = "volume_down"
        
        elif "mute" in command:
            pyautogui.press("volumemute")
            response = "Volume muted."
            action = "mute"
        
        elif "screenshot" in command:
            self.take_screenshot()
            response = "Screenshot taken and saved to desktop."
            action = "screenshot"
        
        elif "wikipedia" in command:
            response = "What would you like to search on Wikipedia?"
            action = "wikipedia"
        
        elif "search for" in command or "google" in command:
            query = command.replace("search for", "").replace("google", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")
            response = f"Searching Google for {query}."
            action = "google_search"
        
        elif "joke" in command:
            jokes = [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Why did the scarecrow win an award? He was outstanding in his field!",
                "Why don't programmers like nature? It has too many bugs!"
            ]
            import random
            response = random.choice(jokes)
            action = "joke"
        
        elif "copy" in command:
            pyautogui.hotkey('ctrl', 'c')
            response = "Copied."
            action = "copy"
        
        elif "paste" in command:
            pyautogui.hotkey('ctrl', 'v')
            response = "Pasted."
            action = "paste"
        
        elif "save" in command:
            pyautogui.hotkey('ctrl', 's')
            response = "Saved."
            action = "save"
        
        else:
            response = "I'm not sure how to help with that."
            action = "unknown"
        
        self.speak(response)
        return {"status": "success", "response": response, "action": action, "command": command}

    def open_application(self, app_name):
        quick_apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "explorer": "explorer.exe"
        }
        
        for app_key, app_exe in quick_apps.items():
            if app_key in app_name.lower():
                subprocess.Popen(app_exe, shell=True)
                return
        
        subprocess.Popen(app_name, shell=True)

    def close_application(self, app_name):
        if not app_name or app_name == "window":
            pyautogui.hotkey('alt', 'f4')
            return
        
        for proc in psutil.process_iter(['name']):
            try:
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    break
            except:
                pass

    def list_windows(self):
        windows = []
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name']
                if proc_name.endswith('.exe') and proc_name not in windows:
                    windows.append(proc_name.replace('.exe', ''))
            except:
                pass
        return [w for w in windows if w.lower() not in ['svchost', 'system', 'registry']]

    def take_screenshot(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        desktop = Path.home() / "Desktop"
        screenshot_path = desktop / f"screenshot_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)

assistant = VoiceAssistantWeb()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listen', methods=['POST'])
def listen():
    try:
        command = assistant.listen_for_command()
        if command:
            result = assistant.process_command(command)
            return jsonify(result)
        else:
            return jsonify({"status": "no_command", "response": "I didn't hear anything. Please try again."})
    except Exception as e:
        return jsonify({"status": "error", "response": f"Error: {str(e)}"})

@app.route('/execute', methods=['POST'])
def execute():
    try:
        data = request.json
        command = data.get('command', '').lower()
        result = assistant.process_command(command)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "response": f"Error: {str(e)}"})

if __name__ == '__main__':
    print("Starting Chanakya - Voice Assistant Web Interface...")
    print("Open your browser to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
