import pygame
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import json
import os
import threading
import time

class DailyRoutineGame:
    def __init__(self, screen):
        self.screen = screen
        self.WIDTH, self.HEIGHT = self.screen.get_size()
        self.FONT = pygame.font.SysFont(None, 36)
        self.clock = pygame.time.Clock()
        self.model = Model("game2/model")
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.q = queue.Queue()
        self.current_text = "Welcome!"
        self.current_level = 0
        self.level_done = False
        self.wait_time = 3
        self.last_transition = time.time()
        self.running = True

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
            {"prompt": "Say 'sleep' or 'mobile'", "correct": "sleep", "success": "Good night! Sweet dreams.", "fail": "No mobile now. Time to sleep."},
        ]

        threading.Thread(target=self.listen, daemon=True).start()

    def audio_callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def listen(self):
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=self.audio_callback):
            while self.running:
                data = self.q.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").lower()
                    if text:
                        print("Heard:", text)
                        self.handle_command(text)

    def load_sound(self, file):
        return pygame.mixer.Sound(file)

    def play_audio(self, level_index, category):
        filename = f"game2/voice_lines/{category}_level{level_index}.ogg"
        if os.path.exists(filename):
            pygame.mixer.stop()
            sound = self.load_sound(filename)
            sound.play()
            while pygame.mixer.get_busy():
                pygame.time.wait(100)

    def handle_command(self, cmd):
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
        while self.running:
            self.screen.fill((0, 0, 50))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            display_text = self.levels[self.current_level]["prompt"] if not self.level_done else self.current_text
            text_surface = self.FONT.render(display_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (self.WIDTH // 2 - text_surface.get_width() // 2, self.HEIGHT // 2))
            pygame.display.flip()
            self.clock.tick(30)

            if self.level_done is False:
                self.play_audio(self.current_level, "prompt")
                self.level_done = None

            if self.level_done and (time.time() - self.last_transition > self.wait_time):
                self.current_level += 1
                if self.current_level >= len(self.levels):
                    self.current_text = "Game Over! You did great."
                    print(self.current_text)
                    time.sleep(3)
                    self.running = False
                else:
                    self.current_text = ""
                    self.level_done = False

        pygame.quit()