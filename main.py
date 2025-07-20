import pygame
import os
import time
import queue

# Imports for the games themselves are moved into the main loop
# to prevent loading them until they are selected.

# --- Constants ---
WIDTH, HEIGHT = 800, 600
COLOR_BG = (20, 20, 40)
COLOR_TITLE = (255, 255, 255)
COLOR_TEXT = (200, 200, 220)

def sanitize_filename(text):
    return text.lower().replace(" ", "").replace(":", "").replace("!", "").replace("'", "")

def load_speech_files():
    """Loads all pre-generated speech files from the 'speech' folder."""
    speech = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    speech_dir = os.path.join(script_dir, "speech")
    print(f"--- Loading All Speech from 'speech' ---")
    if not os.path.isdir(speech_dir):
        print("FATAL: 'speech' directory not found. Please run generate_speech.py first.")
        return None
    for filename in os.listdir(speech_dir):
        if filename.endswith(".wav") or filename.endswith(".mp3"):
            key = os.path.splitext(filename)[0]
            try:
                speech[key] = pygame.mixer.Sound(os.path.join(speech_dir, filename))
            except pygame.error as e:
                print(f"  - Error loading speech '{filename}': {e}")
    print("------------------------------------")
    return speech

def main():
    """Main function to run the game launcher menu."""
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.set_num_channels(2) # 0 for effects, 1 for speech
    speech_channel = pygame.mixer.Channel(1)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game Launcher")
    title_font = pygame.font.SysFont("helvetica", 72)
    option_font = pygame.font.SysFont("helvetica", 48)
    clock = pygame.time.Clock()

    speech_sounds = load_speech_files()
    if not speech_sounds:
        return # Exit if speech files are missing

    speech_queue = queue.Queue()

    def say(text):
        sanitized_key = sanitize_filename(text)
        if sanitized_key in speech_sounds:
            speech_queue.put(speech_sounds[sanitized_key])
        else:
            print(f"Menu Warning: Speech sound not found for key: '{sanitized_key}'")

    # --- Announce Menu ---
    say("Welcome to the Games Portal")
    say("Please select a game")
    say("Press 1 for Audio Memory Tiles")
    say("Press 2 for Daily Routine Adventure")
    say("Press Escape to quit")

    running = True
    while running:
        # --- Speech Playback ---
        if not speech_channel.get_busy() and not speech_queue.empty():
            speech_channel.play(speech_queue.get())

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_1:
                    print("Starting Memory Game...")
                    try:
                        # Corrected import statement
                        from memory_tiles.memory_tiles import MemoryGame
                        game = MemoryGame(screen, speech_sounds)
                        game.run()
                    except ImportError as e:
                        print(f"Could not start Memory Game. Error: {e}")
                        say("Error starting game.")
                    
                    # After game finishes, re-announce menu
                    say("Please select a game")
                    say("Press 1 for Audio Memory Tiles")
                    say("Press 2 for Daily Routine Adventure")
                    say("Press Escape to quit")

                if event.key == pygame.K_2:
                    print("Starting Daily Routine Game...")
                    try:
                        # Import the game only when it's selected
                        from game2.daily_routine_game import DailyRoutineGame
                        game = DailyRoutineGame(screen)
                        game.run()
                    except (ImportError, FileNotFoundError) as e:
                        print(f"Could not start Daily Routine Game. Error: {e}")
                        say("Error starting game. Please check model files and dependencies.")
                    
                    # After game finishes, re-announce menu
                    say("Please select a game")
                    say("Press 1 for Audio Memory Tiles")
                    say("Press 2 for Daily Routine Adventure")
                    say("Press Escape to quit")

        # --- Drawing ---
        screen.fill(COLOR_BG)
        title_surf = title_font.render("Game Launcher", True, COLOR_TITLE)
        screen.blit(title_surf, (WIDTH/2 - title_surf.get_width()/2, 100))

        option1_surf = option_font.render("1: Audio Memory Tiles", True, COLOR_TEXT)
        screen.blit(option1_surf, (WIDTH/2 - option1_surf.get_width()/2, 250))
        
        option2_surf = option_font.render("2: Daily Routine Adventure", True, COLOR_TEXT)
        screen.blit(option2_surf, (WIDTH/2 - option2_surf.get_width()/2, 350))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
