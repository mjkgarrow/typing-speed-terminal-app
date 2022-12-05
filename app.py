import curses
import time
import os
import textwrap
import requests
import random


# Finding the terminal window size to correctly center text
WINDOW_SIZE = [os.get_terminal_size()[0], os.get_terminal_size()[1]]
MAX_WIDTH = int(WINDOW_SIZE[0]//1.3)
TEXT_START_X = int((WINDOW_SIZE[0] - MAX_WIDTH)//2)
TEXT_START_Y = int(WINDOW_SIZE[1] * 0.2)


def load_file():
    '''Loads txt file from within app directory, returns a string of file contents'''
    directory = os.getcwd()
    while True:
        for file in os.listdir(directory):
            if file.endswith(".txt") and file != "requirements.txt":
                with open(file, 'r') as f:
                    lines = f.read().splitlines()
                    return " ".join(lines)


def quick_print(window, x, y, text):
    ''' Clears screen and types supplied text'''
    window.erase()
    window.addstr(
        y, x, text)
    window.refresh()


def menu(window, x, y):
    ''' Displays menu for user to select an option, returns a typing prompt based on the option'''
    while True:
        menu_text = ["Welcome to Speed-Typer, a typing game to test your skills",
                     "Please select from the following options:",
                     "1. Test from file",
                     "2. Test random words",
                     "3. Test a quote",
                     "4. Quit"]

        window.erase()

        for i in range(len(menu_text)):
            window.addstr(y + i, x, menu_text[i])

        key = window.getch()

        match key:
            case 49:
                quick_print(
                    window, x, y, "Copy '.txt' file to app directory to load text")
                file_text = load_file()
                return textwrap.wrap(file_text, MAX_WIDTH)
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
                return textwrap.wrap(" ".join(word_selection), MAX_WIDTH)
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
                return textwrap.wrap(f"{quote['text']} - {quote['author']}", MAX_WIDTH)
            case 52:
                quick_print(
                    window, x, y, "Goodbye")
                time.sleep(1)
                quit()


def draw(window, text):
    '''Draws text to the screen, line by line'''
    window.addstr(0, 0, "Press 'esc' to exit, 'enter' to return to menu")
    for i in range(len(text)):
        window.addstr(TEXT_START_Y + i, TEXT_START_X,
                      text[i])
    # window.move(TEXT_START_Y, TEXT_START_X)


def main(window):
    # Set cursor to invisible
    curses.curs_set(0)

    # Ask user for menu choice, return a typing prompt
    typing_prompt = menu(window, TEXT_START_X, TEXT_START_Y)

    # Update delay so that program isn't waiting on user input
    window.nodelay(True)

    # Clear screen of menu
    window.erase()

    # Applying text styling colours to variables
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    white = curses.color_pair(1)
    green = curses.color_pair(2)
    red = curses.color_pair(3)

    # Variable to store user input
    user_typed_string = ""

    while True:
        # Get the inputted key from user
        try:
            key = window.getch()
        except:
            key = None

        # Check if key is 'esc', quits immediately
        if key == 27:
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
            try:
                user_typed_string = user_typed_string[:-1]
            except:
                continue

        # Draw typing prompt to screen
        draw(window, typing_prompt)

        # Make text wrapped so it will fit in center of screen
        wrapped_user_typed = textwrap.wrap(user_typed_string, MAX_WIDTH)

        # Draw user input
        draw(window, wrapped_user_typed)

        # Display new content
        window.refresh()


if __name__ == "__main__":
    # Sets delay on escape key to 25 milliseconds
    os.environ.setdefault("ESCDELAY", "25")

    # Calls the main function
    curses.wrapper(main)
