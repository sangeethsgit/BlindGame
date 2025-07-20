import pygame
import random
import time
import os
import queue

# --- Game Constants ---
SOUND_PAIRS = [
    "Cat", "Dog", "Bird", "Cow",
    "Car", "Bell", "Drum", "Duck"
]
GRID_SIZE = 4
TILE_COUNT = GRID_SIZE * GRID_SIZE
TILE_SIZE = 120
MARGIN = 20
WINDOW_WIDTH = (TILE_SIZE + MARGIN) * GRID_SIZE + MARGIN
WINDOW_HEIGHT = (TILE_SIZE + MARGIN) * GRID_SIZE + MARGIN
COLOR_BG = (30, 30, 30)
COLOR_HIDDEN = (70, 70, 70)
COLOR_REVEALED = (255, 215, 0)
COLOR_MATCHED = (60, 179, 113)
COLOR_TEXT = (255, 255, 255)
KEY_MAP = {
    pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3,
    pygame.K_q: 4, pygame.K_w: 5, pygame.K_e: 6, pygame.K_r: 7,
    pygame.K_a: 8, pygame.K_s: 9, pygame.K_d: 10, pygame.K_f: 11,
    pygame.K_z: 12, pygame.K_x: 13, pygame.K_c: 14, pygame.K_v: 15,
}

# --- Main Game Class ---
class MemoryGame:
    # The __init__ method is updated to accept the screen and speech_sounds from the main menu
    def __init__(self, screen, speech_sounds):
        # Use the screen and sounds passed from the main menu
        self.screen = screen
        self.speech_sounds = speech_sounds
        
        # Game-specific setup
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.effects_channel = pygame.mixer.Channel(0)
        self.speech_channel = pygame.mixer.Channel(1)
        self.speech_queue = queue.Queue()
        
        # Load game-specific sounds
        self.sounds = self.load_sounds("sounds", SOUND_PAIRS)
        self.reset_game_state()

    def reset_game_state(self):
        """Initializes or resets the state of the game."""
        self.tiles = (SOUND_PAIRS * 2)
        random.shuffle(self.tiles)
        self.revealed_state = ['hidden'] * TILE_COUNT
        self.first_selection = None
        self.second_selection = None
        self.running = True
        self.found_pairs = 0
        self.is_checking_match = False
        self.timer_start_time = 0
        self.pending_selection_index = None

    def load_sounds(self, folder, sound_names):
        sounds = {}
        # The path is now relative to the main script's location
        script_dir = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
        sounds_dir = os.path.join(script_dir, "memory_tiles", folder)
        
        print(f"--- Loading Sounds from '{folder}' ---")
        print(f"Looking in: {sounds_dir}")

        if not os.path.isdir(sounds_dir):
            print(f"Warning: '{folder}' directory not found.")
            return sounds

        for name in sound_names:
            path = os.path.join(sounds_dir, f"{name}.wav")
            if not os.path.exists(path):
                path = os.path.join(sounds_dir, f"{name}.mp3")
            
            if os.path.exists(path):
                try:
                    sounds[name] = pygame.mixer.Sound(path)
                    print(f"  - Loaded {name}")
                except pygame.error as e:
                    print(f"  - Error loading {name}: {e}")
            else:
                print(f"  - Warning: Sound file not found for {name}")
        print("-----------------------------")
        return sounds

    def sanitize_filename(self, text):
        return text.lower().replace(" ", "").replace(":", "").replace("!", "").replace("'", "")

    def say(self, text):
        sanitized_key = self.sanitize_filename(text)
        if sanitized_key in self.speech_sounds:
            self.speech_queue.put(self.speech_sounds[sanitized_key])
        else:
            print(f"Warning: Speech sound not found for key: '{sanitized_key}'")

    def stop_all_sounds(self):
        self.effects_channel.stop()
        self.speech_channel.stop()
        with self.speech_queue.mutex:
            self.speech_queue.queue.clear()

    def introduce_game(self):
        self.draw_board()
        self.say("Welcome to Audio Memory Tiles")
        self.say("Let's begin")
        self.say("Use 1 to 4, Q to R, etc.")
        self.say("Press I at any time to hear the current score")
        self.say("Press the Spacebar to stop the current sound")
        self.say("Press Escape at any time to quit")

    def draw_board(self):
        self.screen.fill(COLOR_BG)
        for i in range(TILE_COUNT):
            row, col = i // GRID_SIZE, i % GRID_SIZE
            x, y = MARGIN + col * (TILE_SIZE + MARGIN), MARGIN + row * (TILE_SIZE + MARGIN)
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            color = COLOR_HIDDEN
            if self.revealed_state[i] == 'revealed': color = COLOR_REVEALED
            elif self.revealed_state[i] == 'matched': color = COLOR_MATCHED
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            if self.revealed_state[i] != 'hidden':
                text_surf = self.font.render(self.tiles[i], True, COLOR_TEXT)
                text_rect = text_surf.get_rect(center=rect.center)
                self.screen.blit(text_surf, text_rect)
        pygame.display.flip()

    def handle_input(self, event):
        if event.key == pygame.K_i:
            self.stop_all_sounds()
            self.say("Score"); self.say(str(self.found_pairs)); self.say("of"); self.say(str(len(SOUND_PAIRS)))
            return
        if event.key in KEY_MAP:
            index = KEY_MAP[event.key]
            self.stop_all_sounds()
            self.say(pygame.key.name(event.key).upper())
            if self.revealed_state[index] == 'matched':
                self.say("That tile is already matched. Try another.")
                if self.first_selection:
                    self.say("Your first choice was a")
                    self.effects_channel.play(self.sounds[self.first_selection[1]], maxtime=3000)
                return
            if self.first_selection and self.first_selection[0] == index:
                self.say("You picked the same tile again. Choose a different one.")
                return
            self.pending_selection_index = index

    def process_selection(self, index):
        sound_name = self.tiles[index]
        self.revealed_state[index] = 'revealed'
        self.draw_board()
        if sound_name in self.sounds:
            self.effects_channel.play(self.sounds[sound_name], maxtime=3000)
        else: self.say(f"Sound for {sound_name} not found.")
        if self.first_selection is None: self.first_selection = (index, sound_name)
        else: self.second_selection = (index, sound_name); self.check_for_match()

    def check_for_match(self):
        self.is_checking_match = True
        self.timer_start_time = pygame.time.get_ticks()

    def resolve_match(self):
        idx1, sound1 = self.first_selection
        idx2, sound2 = self.second_selection
        if sound1 == sound2:
            self.say("It's a match!")
            self.revealed_state[idx1] = 'matched'
            self.revealed_state[idx2] = 'matched'
            self.found_pairs += 1
            self.say("Score"); self.say(str(self.found_pairs)); self.say("of"); self.say(str(len(SOUND_PAIRS)))
            if self.found_pairs == len(SOUND_PAIRS):
                self.draw_board()
                self.say("Congratulations! You found all the pairs. You win!")
                self.running = False
        else:
            self.say("Try again")
            self.revealed_state[idx1] = 'hidden'
            self.revealed_state[idx2] = 'hidden'
        self.first_selection, self.second_selection = None, None
        self.is_checking_match = False

    def run(self):
        self.reset_game_state()
        self.introduce_game()
        while self.running:
            if not self.speech_channel.get_busy() and not self.speech_queue.empty():
                self.speech_channel.play(self.speech_queue.get())
            if self.pending_selection_index is not None and self.speech_queue.empty() and not self.speech_channel.get_busy():
                self.process_selection(self.pending_selection_index)
                self.pending_selection_index = None
            if self.is_checking_match and not self.effects_channel.get_busy() and not self.speech_channel.get_busy() and pygame.time.get_ticks() - self.timer_start_time >= 1000:
                self.resolve_match()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False; self.stop_all_sounds()
                    elif event.key == pygame.K_SPACE: self.stop_all_sounds()
                    elif not self.is_checking_match and self.pending_selection_index is None and self.speech_queue.empty():
                        self.handle_input(event)
            self.draw_board()
            self.clock.tick(30)
        self.stop_all_sounds()
        self.say("Returning to main menu.")
        time.sleep(2)
