import pygame
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import json
import os
import threading
import time

# ------------ Setup Vosk Model ----------------
if not os.path.exists("model"):
    print("Please download a model from https://alphacephei.com/vosk/models and unzip into 'model'")
    exit(1)

model = Model("model")
recognizer = KaldiRecognizer(model, 16000)
q = queue.Queue()

def audio_callback(indata, frames, time, status):
    q.put(bytes(indata))

def listen():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()
                if text:
                    print("Heard:", text)
                    handle_command(text)

# ------------ Pygame Setup ---------------------
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 700, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Daily Routine Game")
FONT = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

# ------------ Game Levels -----------------------
levels = [
    {
        "prompt": "Say 'wake up' or 'sleep more'",
        "correct": "wake up",
        "success": "Good morning! You woke up on time.",
        "fail": "You can't sleep more. Let's wake up now.",
    },
    {
        "prompt": "Say 'brush' or 'play'",
        "correct": "brush",
        "success": "Nice! Brushing keeps teeth healthy.",
        "fail": "No play now. First, let's brush.",
    },
    {
        "prompt": "Say 'bath' or 'mobile'",
        "correct": "bath",
        "success": "Refreshing! Bath time it is.",
        "fail": "No mobile now. Take a bath.",
    },
    {
        "prompt": "Say 'uniform' or 'pajamas'",
        "correct": "uniform",
        "success": "Perfect! Let's wear the uniform.",
        "fail": "No pajamas now. Wear uniform.",
    },
    {
        "prompt": "Say 'breakfast' or 'chips'",
        "correct": "breakfast",
        "success": "Healthy breakfast! Well done.",
        "fail": "Not chips now. Have breakfast.",
    },
    {
        "prompt": "Say 'school bag' or 'video game'",
        "correct": "school bag",
        "success": "Great! Packing the school bag.",
        "fail": "No video games now. Pick school bag.",
    },
    {
        "prompt": "Say 'bus stop' or 'TV'",
        "correct": "bus stop",
        "success": "Smart! Heading to bus stop.",
        "fail": "No TV now. Go to bus stop.",
    },
    {
        "prompt": "Say 'greet teacher' or 'run'",
        "correct": "greet teacher",
        "success": "Nice manners! Greeted the teacher.",
        "fail": "No running. Greet your teacher.",
    },
    {
        "prompt": "Say 'attend class' or 'sleep'",
        "correct": "attend class",
        "success": "Focused! Attending class now.",
        "fail": "No sleeping. Attend your class.",
    },
    {
        "prompt": "Say 'lunch' or 'candy'",
        "correct": "lunch",
        "success": "Healthy lunch time!",
        "fail": "No candy now. Have lunch.",
    },
    {
        "prompt": "Say 'playground' or 'canteen'",
        "correct": "playground",
        "success": "Great! Recess fun in playground.",
        "fail": "No canteen today. Let's play.",
    },
    {
        "prompt": "Say 'say bye' or 'throw bag'",
        "correct": "say bye",
        "success": "Polite! You said bye to friends.",
        "fail": "Don't throw bag! Say bye nicely.",
    },
    {
        "prompt": "Say 'homework' or 'cartoon'",
        "correct": "homework",
        "success": "Responsible! Starting homework.",
        "fail": "No cartoon now. Do homework.",
    },
    {
        "prompt": "Say 'dinner' or 'ice cream'",
        "correct": "dinner",
        "success": "Yum! Time for dinner.",
        "fail": "No ice cream now. Have dinner.",
    },
    {
        "prompt": "Say 'sleep' or 'mobile'",
        "correct": "sleep",
        "success": "Good night! Sweet dreams.",
        "fail": "No mobile now. Time to sleep.",
    }
]

# ------------ Audio Handling ---------------------
def load_sound(file):
    return pygame.mixer.Sound(file)

def play_audio(level_index, category):  # category: prompt/success/fail
    filename = f"voice_lines/{category}_level{level_index}.ogg"
    if os.path.exists(filename):
        pygame.mixer.stop()  # Stop other sounds
        sound = load_sound(filename)
        sound.play()
        while pygame.mixer.get_busy():
            pygame.time.wait(100)  # Wait for the sound to finish

# ------------ Game State ------------------------
current_text = "Welcome!"
current_level = 0
level_done = False

def handle_command(cmd):
    global current_level, current_text, level_done
    level = levels[current_level]
    if level["correct"] in cmd:
        current_text = level["success"]
        play_audio(current_level, "success")
    else:
        current_text = level["fail"]
        play_audio(current_level, "fail")
    
    level_done = True

# ------------ Start Listening Thread ------------
listen_thread = threading.Thread(target=listen, daemon=True)
listen_thread.start()

# ------------ Main Loop -------------------------
running = True
wait_time = 3
last_transition = time.time()

while running:
    screen.fill((0, 0, 50))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Display prompt or result
    display_text = levels[current_level]["prompt"] if not level_done else current_text
    text_surface = FONT.render(display_text, True, (255, 255, 255))
    screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(30)

    # Play prompt audio once per level
    if level_done is False:
        play_audio(current_level, "prompt")
        level_done = None

    # Wait before moving to next level
    if level_done and (time.time() - last_transition > wait_time):
        current_level += 1
        if current_level >= len(levels):
            current_text = "Game Over! You did great."
            print(current_text)
            running = False
        else:
            current_text = ""
            level_done = False
            last_transition = time.time()

pygame.quit()