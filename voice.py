import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipediaapi
import time
import sys

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
        
        self.speak(f"{greeting} How can I assist you today?")

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
