import pyautogui
import time

# List of sentences to type
sentences = [
    "we are unlucky watching this live"

]

# Delay to allow you to focus on the input area where the text will be typed
print("Place your cursor in the desired input area. Starting in 5 seconds...")
time.sleep(10)

#ype each sentence and press Enter
for i in range(10):
       for sentence in sentences:
         pyautogui.typewrite(sentence)  # Type the sentence at the cursor position
         pyautogui.press("enter")  # Simulate pressing the Enter key
    # Optional: Wait a second between sentences
hi
hi
hi
hi
hi
hi
hi
hi
hi
hi
