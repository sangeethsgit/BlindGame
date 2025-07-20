import pygame
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import json
import os
import threading
import time

# --- Constants ---
WIDTH, HEIGHT = 700, 480
FONT_SYS = None # Will be initialized with pygame

class DailyRoutineGame:
    def __init__(self, screen):
        self.screen = screen
        global FONT_SYS
        if FONT_SYS is None: FONT_SYS = pygame.font.SysFont(None, 36)
        self.font = FONT_SYS
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game content
        self.levels = [
            {"prompt": "Say 'wake up' or 'sleep more'", "correct": "wake up", "success": "Good morning! You woke up on time.", "fail": "You can't sleep more. Let's wake up now."},
            {"prompt": "Say 'brush' or 'play'", "correct": "brush", "success": "Nice! Brushing keeps teeth healthy.", "fail": "No play now. First, let's brush."},
            {"prompt": "Say 'bath' or 'mobile'", "correct": "bath", "success": "Refreshing! Bath time it is.", "fail": "No mobile now. Take a bath."},
            {"prompt": "Say 'uniform' or 'pajamas'", "correct": "uniform", "success": "Perfect! Let's wear the uniform.", "fail": "No pajamas now. Wear uniform."},
            {"prompt": "Say 'breakfast' or 'chips'", "correct": "breakfast", "success": "Healthy breakfast! Well done.", "fail": "Not chips now. Have breakfast."},
            {"prompt": "Say 'school bag' or 'video game'", "correct": "school bag", "success": "Great! Packing the school bag.", "fail": "No video games now. Pick school bag."},
            {"prompt": "Say 'bus stop' or 'TV'", "correct": "bus stop", "success": "Smart! Heading to bus stop.", "fail": "No TV now. Go to bus stop."},
            {"prompt": "Say 'greet teacher' or 'run'", "correct": "greet teacher", "success": "Nice manners! Greeted the teacher.", "fail": "No running. Greet your teacher."},
            {"prompt": "Say 'attend class' or 'sleep'", "correct": "attend class", "success": "Focused! Attending class now.", "fail": "No sleeping. Attend your class."},
            {"prompt": "Say 'lunch' or 'candy'", "correct": "lunch", "success": "Healthy lunch time!", "fail": "No candy now. Have lunch."},
            {"prompt": "Say 'playground' or 'canteen'", "correct": "playground", "success": "Great! Recess fun in playground.", "fail": "No canteen today. Let's play."},
            {"prompt": "Say 'say bye' or 'throw bag'", "correct": "say bye", "success": "Polite! You said bye to friends.", "fail": "Don't throw bag! Say bye nicely."},
            {"prompt": "Say 'homework' or 'cartoon'", "correct": "homework", "success": "Responsible! Starting homework.", "fail": "No cartoon now. Do homework."},
            {"prompt": "Say 'dinner' or 'ice cream'", "correct": "dinner", "success": "Yum! Time for dinner.", "fail": "No ice cream now. Have dinner."},
            {"prompt": "Say 'sleep' or 'mobile'", "correct": "sleep", "success": "Good night! Sweet dreams.", "fail": "No mobile now. Time to sleep."}
        ]
        
        # Game state
        self.current_text = "Welcome to Daily Routine Adventure!"
        self.current_level = 0
        self.level_done = False
        self.last_transition = time.time()
        self.wait_time = 3

        # --- Vosk setup moved inside __init__ ---
        self.vosk_q = queue.Queue()
        self.recognizer = None
        
        # This path now correctly looks for the 'model' folder inside the 'game2' directory.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "model")
        
        if not os.path.exists(model_path):
            # Instead of exiting, we raise an error that the main menu can catch.
            raise FileNotFoundError(f"Vosk model not found. Please ensure the 'model' folder is inside the 'game2' folder. Looked in: {model_path}")
        
        model = Model(model_path)
        self.recognizer = KaldiRecognizer(model, 16000)
        
        self.listen_thread = threading.Thread(target=self.listen, daemon=True)

    def audio_callback(self, indata, frames, time, status):
        if self.running:
            self.vosk_q.put(bytes(indata))

    def listen(self):
        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=self.audio_callback):
                while self.running:
                    data = self.vosk_q.get()
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "").lower()
                        if text:
                            print("Heard:", text)
                            self.handle_command(text)
        except Exception as e:
            print(f"Error in audio listening thread: {e}")

    def play_audio(self, level_index, category):
        # This function assumes you have pre-generated audio files.
        # It needs to be implemented if you have them.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "voice_lines", f"{category}_level{level_index}.ogg")
        if os.path.exists(filename):
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)

    def handle_command(self, cmd):
        if self.level_done is not False: return
        level = self.levels[self.current_level]
        if level["correct"] in cmd:
            self.current_text = level["success"]
            self.play_audio(self.current_level, "success")
        else:
            self.current_text = level["fail"]
            self.play_audio(self.current_level, "fail")
        self.level_done = True
        self.last_transition = time.time()

    def run(self):
        if not self.recognizer:
            print("Recognizer not initialized. Cannot run game.")
            return

        self.listen_thread.start()
        
        while self.running:
            self.screen.fill((0, 0, 50))
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.running = False

            display_text = self.levels[self.current_level]["prompt"] if not self.level_done else self.current_text
            text_surface = self.font.render(display_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            self.clock.tick(30)

            if self.level_done is False:
                self.play_audio(self.current_level, "prompt")
                self.level_done = None # Mark prompt as played

            if self.level_done and (time.time() - self.last_transition > self.wait_time):
                self.current_level += 1
                if self.current_level >= len(self.levels):
                    self.current_text = "Game Over! You did great."
                    self.running = False
                else:
                    self.level_done = False
                    self.last_transition = time.time()
        
        print("Returning to main menu.")
        # Ensure the listening thread stops by setting running to False
        self.running = False
