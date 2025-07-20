import pyttsx3
import os

# Folder to save generated .wav files
OUTPUT_FOLDER = "speech"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# List of texts you want to generate as speech files
phrases = [
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
]


tile_keys = [str(i) for i in range(1, 5)] + ["Q", "W", "E", "R", "A", "S", "D", "F", "Z", "X", "C", "V"]


scores = [f"Score {i}" for i in range(0, 9)]
ofs = [f"of {i}" for i in range(1, 9)]

# Combine all text
all_phrases = phrases + tile_keys + scores + ofs

# Initialize pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speaking rate

def sanitize(text):
    return text.lower().replace(" ", "").replace(":", "").replace("!", "").replace("'", "")

for phrase in all_phrases:
    filename = sanitize(phrase) + ".wav"
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    print(f"Generating: {filepath}")
    engine.save_to_file(phrase, filepath)

engine.runAndWait()
print("✅ All speech files generated in 'speech/' folder.")
