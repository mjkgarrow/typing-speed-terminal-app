import curses
import time
import os
import textwrap
import requests
import random


# Create requirements
# pip freeze > requirements.txt

# Finding the terminal window size to correctly center text
WINDOW_SIZE = [os.get_terminal_size()[0], os.get_terminal_size()[1]]
MAX_WIDTH = int(WINDOW_SIZE[0]//1.3)
TEXT_START_X = int((WINDOW_SIZE[0] - MAX_WIDTH)//2)
TEXT_START_Y = int(WINDOW_SIZE[1] * 0.2)

# Working folder director
DIRECTORY = os.getcwd()


def load_file():
    '''Loads prompt txt file from within app directory, returns a string of file contents'''
    while True:
        for file in os.listdir(DIRECTORY):
            if file.endswith(".txt") and (file != "requirements.txt" and file != "scores.txt"):
                with open(file, 'r') as f:
                    lines = f.read().splitlines()
                    return " ".join(lines)


def load_high_score():
    ''' Loads scores file and returns list of scores'''
    file_list = os.listdir(DIRECTORY)
    if "scores.txt" in file_list:
        with open("scores.txt", 'r') as f:
            return f.read().splitlines()

    else:
        return ["No high scores."]


def quick_print(window, x, y, text):
    ''' Clears screen and types supplied text'''
    window.erase()
    window.addstr(
        y, x, text)
    window.refresh()


def draw(window, text):
    '''Draws list of text to the screen, line by line'''
    for i in range(len(text)):
        window.addstr(TEXT_START_Y + i, TEXT_START_X,
                      text[i])


def calculate_wpm(wrapped_user_typed):
    pass


def print_screen(window, typing_prompt, wrapped_user_typed):

    # Draw typing prompt to screen
    draw(window, typing_prompt)

    # Draw user input
    for line in range(len(wrapped_user_typed)):
        for char in range(len(wrapped_user_typed[line])):
            colour = curses.color_pair(2)
            if wrapped_user_typed[line][char] != typing_prompt[line][char]:
                colour = curses.color_pair(3)
            window.addstr(TEXT_START_Y + line, TEXT_START_X + char,
                          wrapped_user_typed[line][char], colour)


def menu(window, x, y):
    ''' Displays menu for user to select an option, returns a typing prompt based on the option'''
    # Update delay so that program waits on user input
    window.nodelay(False)

    # Set cursor to invisible
    curses.curs_set(0)

    while True:
        menu_text = ["Welcome to Keebz-Typerz, a typing game to test your skills",
                     "Please select a number from the following options:",
                     "1. Test from file",
                     "2. Test random words",
                     "3. Test a quote",
                     "4. See high scores",
                     "5. Quit"]

        window.erase()

        for i in range(len(menu_text)):
            window.addstr(y + i, x, menu_text[i])

        key = window.getch()

        match key:
            case 49:
                quick_print(
                    window, x, y, "Copy '.txt' file to app directory to load text")
                file_text = load_file()
                return textwrap.wrap(file_text, MAX_WIDTH, drop_whitespace=False)
            case 50:
                quick_print(
                    window, x, y, "Loading words from MIT")
                try:
                    response = requests.get(
                        "https://www.mit.edu/~ecprice/wordlist.10000")
                except:
                    quick_print(
                        window, x, y, "Unable to load random words, sorry!")
                    continue
                random_words = response.content.splitlines()
                word_selection = []
                for i in range(50):
                    word_selection.append(
                        str(random_words[random.randint(0, len(random_words))])[2:-1])
                return textwrap.wrap(" ".join(word_selection), MAX_WIDTH, drop_whitespace=False)
            case 51:
                quick_print(
                    window, x, y, "Loading quotes from Type.fit API")
                try:
                    response = requests.get(
                        "https://type.fit/api/quotes").json()
                except:
                    quick_print(window, x, y, "Unable to load quotes, sorry!")
                    continue
                quote = response[random.randint(0, len(response))]
                return textwrap.wrap(f"{quote['text']} - {quote['author']}", MAX_WIDTH, drop_whitespace=False)
            case 52:
                scores = load_high_score()
                window.erase()
                window.addstr(
                    0, 0, "Press 'esc' to exit, 'enter' to return to menu")
                draw(window, scores)
                window.refresh()
                window.getch()
            case 53:
                quick_print(
                    window, x, y, "Goodbye")
                time.sleep(1)
                quit()

        window.refresh()


def main(window):
    # Applying text styling colours to variables
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # white text
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # green text
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)  # red text
    white = curses.color_pair(1)
    green = curses.color_pair(2)
    red = curses.color_pair(3)

    # Ask user for menu choice, return a typing prompt
    typing_prompt = menu(window, TEXT_START_X, TEXT_START_Y)

    # # Set cursor to visible
    # curses.curs_set(1)

    # Update delay so that program isn't waiting on user input
    window.nodelay(True)

    # Variable to store user input
    user_typed_string = ""

    while True:
        # Get the inputted key from user, because delay is zero getch() will be returning None continuously until user types.
        # So need to catch that possible error.
        try:
            key = window.getch()
        except:
            key = None

        # Check if key is 'esc', quits immediately
        if key == 27:
            quick_print(window, TEXT_START_X, TEXT_START_Y, "Goodbye")
            time.sleep(1)
            quit()
        # Check if 'enter' key hit, clears input and returns to main menu
        if key == 10 or key == 13:
            user_typed_string = ""
            typing_prompt = menu(window, TEXT_START_X, TEXT_START_Y)
        # Check if key is alphanumeric/punctuation, add to user input
        elif 32 <= key < 126:
            user_typed_string += chr(key)
        # Check if key is backspace, remove from user input
        elif key == 127:
            if len(user_typed_string) > 0:
                user_typed_string = user_typed_string[:-1]

        # Make text wrapped so it will fit in center of screen
        wrapped_user_typed = textwrap.wrap(
            user_typed_string, MAX_WIDTH, drop_whitespace=False)

        # Clear screen so new text can be drawn
        window.erase()

        # Draw menu directions to screen
        window.addstr(0, 0, "Press 'esc' to exit, 'enter' to return to menu")

        print_screen(window, typing_prompt, wrapped_user_typed)

        # Display new content
        window.refresh()


if __name__ == "__main__":
    # Sets delay on escape key to 25 milliseconds
    os.environ.setdefault("ESCDELAY", "25")

    # Calls the main function
    curses.wrapper(main)
