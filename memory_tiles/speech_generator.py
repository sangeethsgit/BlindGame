import pyttsx3
import os

# Folder to save generated .wav files
OUTPUT_FOLDER = "speech"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# This list contains every unique phrase used in main.py and memory_game.py
phrases = [
    # --- Menu phrases from main.py ---
    "Welcome to the Games Portal",
    "Please select a game",
    "Press 1 for Audio Memory Tiles",
    "Press 2 for Daily Routine Adventure",
    "Press Escape to quit",
    "Error starting game.",
    "Error starting game. Please check model files and dependencies.",

    # --- Memory Game phrases ---
    "Welcome to Audio Memory Tiles",
    "Let's begin",
    "Use 1 to 4, Q to R, etc.",
    "Use 1 to 4, Q to R, A to F, etc.",
    "Press I at any time to hear the current score",
    "Press the Spacebar to stop the current sound",
    "It's a match!",
    "Try again",
    "Score",
    "of",
    "Congratulations! You found all the pairs. You win!",
    "Your first choice was a",
    "That tile is already matched. Try another.",
    "You picked the same tile again. Choose a different one.",
    "Goodbye"
]

# Keys and numbers for the memory game
tile_keys_and_numbers = [str(i) for i in range(0, 10)] + ["Q", "W", "E", "R", "A", "S", "D", "F", "Z", "X", "C", "V"]

# Combine all text
all_phrases = phrases + tile_keys_and_numbers

# Initialize pyttsx3
engine = pyttsx3.init(driverName='sapi5')
engine.setProperty('rate', 170)

def sanitize_filename(text):
    """
    This function MUST be identical to the one in main.py and memory_game.py
    It sanitizes text to create a valid filename.
    """
    return text.lower().replace(" ", "").replace(":", "").replace("!", "").replace("'", "").replace(".", "").replace(",", "")

print(f"--- Generating speech files in '{OUTPUT_FOLDER}' folder ---")
for phrase in all_phrases:
    filename = sanitize_filename(phrase) + ".wav"
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    print(f"Generating: {filepath}")
    engine.save_to_file(phrase, filepath)

engine.runAndWait()
print(f"✅ All speech files generated successfully.")
