import pyttsx3
import os

# Folder to save generated .wav files
OUTPUT_FOLDER = "speech"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# List of texts you want to generate as speech files
phrases = [
    # Menu phrases
    "Welcome to the Games Portal",
    "Please select a game",
    "Press 1 for Audio Memory Tiles",
    "Press 2 for Daily Routine Adventure",
    "Press Escape to quit",
    "Invalid selection",

    # Memory Game phrases
    "Welcome to Audio Memory Tiles",
    "Use 1 to 4, Q to R, etc.",
    "It's a match!",
    "Try again",
    "Score",
    "of",
    "You won!",
    "You lost!",
    "Press space to replay",
    "Let's begin",
    "Congratulations! You found all the pairs. You win!",
    "Your first choice was a",
    "That tile is already matched. Try another.",
    "You picked the same tile again. Choose a different one.",
    "Press I at any time to hear the current score",
    "Press the Spacebar to stop the current sound",
    "Goodbye"
]

# Keys and numbers for the memory game
tile_keys = [str(i) for i in range(1, 10)] + ["Q", "W", "E", "R", "A", "S", "D", "F", "Z", "X", "C", "V"]

# Combine all text
all_phrases = phrases + tile_keys

# Initialize pyttsx3
engine = pyttsx3.init(driverName='sapi5')
engine.setProperty('rate', 170)

def sanitize(text):
    """Sanitizes text to create a valid filename."""
    return text.lower().replace(" ", "").replace(":", "").replace("!", "").replace("'", "").replace(".", "")

for phrase in all_phrases:
    filename = sanitize(phrase) + ".wav"
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    print(f"Generating: {filepath}")
    engine.save_to_file(phrase, filepath)

engine.runAndWait()
print(f"✅ All speech files generated in '{OUTPUT_FOLDER}' folder.")
