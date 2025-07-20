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
    print("Please download a model from https://alphacephei.com/vosk/models")
    exit(1)

model = Model("model")
recognizer = KaldiRecognizer(model, 16000)
q = queue.Queue()

# ------------ Mic Thread ----------------------
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
                    handle_voice_command(text)

# ------------ Pygame Setup ---------------------
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Voice Chore Game")

FONT = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

# Load Audio
def load_sound(path):
    return pygame.mixer.Sound(path)

prompt_audio = load_sound("prompt.ogg")
brush_audio = load_sound("brush.ogg")
shirt_audio = load_sound("shirt.ogg")

# ------------ Voice Command Handler ------------
current_text = "Say 'brush' or 'shirt'"

def handle_voice_command(cmd):
    global current_text
    if "brush" in cmd:
        current_text = "Brushing..."
        brush_audio.play()
    elif "shirt" in cmd:
        current_text = "Getting dressed..."
        shirt_audio.play()
    else:
        current_text = "Didn't understand. Try again."

# ------------ Start Listening Thread ------------
listen_thread = threading.Thread(target=listen, daemon=True)
listen_thread.start()

# Play initial prompt
prompt_audio.play()

# ------------ Main Loop -------------------------
running = True
while running:
    screen.fill((30, 30, 30))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw text
    text_surface = FONT.render(current_text, True, (255, 255, 255))
    screen.blit(text_surface, (WIDTH//2 - text_surface.get_width()//2, HEIGHT//2))
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
