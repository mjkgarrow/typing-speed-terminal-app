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


def set_shorter_esc_delay_in_os():
    '''Triggers escape key immediately rather than waiting a second'''
    os.environ.setdefault("ESCDELAY", "25")


def check_key_validity(window):
    while True:
        # Get the inputted key from user
        key = window.getch()

        # Quit if key is 'esc'
        if key == 27:
            quit()

        # Check if key is alphanumeric/punctuation and return it
        elif 32 <= key < 126:
            return chr(key)


def load_file(window):
    directory = os.getcwd()
    for file in os.listdir(directory):
        if file.endswith(".txt") and file != "requirements.txt":
            with open(file, 'r') as f:
                lines = f.read().splitlines()
                return " ".join(lines)


def quick_print(window, x, y, text):
    window.clear()
    window.addstr(
        y, x, text)
    window.refresh()


def menu(window, x, y):
    while True:
        menu_text = ["Welcome to Speed-Typer, a typing game to test your skills",
                     "Please select from the following options:",
                     "1. Test from file",
                     "2. Test random words",
                     "3. Test a quote",
                     "4. Quit"]

        window.clear()

        for i in range(len(menu_text)):
            window.addstr(y + i, x, menu_text[i])

        key = window.getch()

        match key:
            case 49:
                quick_print(
                    window, x, y, "Copy '.txt' file to app directory to load text")
                file_text = load_file(window)
                return [file_text]
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
                return [" ".join(word_selection)]
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
                return [f"{quote['text']} - {quote['author']}"]
            case 52:
                quick_print(
                    window, x, y, "Goodbye")
                time.sleep(1)
                quit()


def main(window):

    # Ask user for menu choice
    typing_prompt = menu(window, TEXT_START_X, TEXT_START_Y)

    # Update delay so that program isn't waiting on user input
    window.nodelay(True)

    # Clear screen of menu
    window.clear()

    # Applying text styling colours to variables
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    white = curses.color_pair(1)
    green = curses.color_pair(2)
    red = curses.color_pair(3)

    while True:
        # Get the inputted key from user
        try:
            key = window.getch()
        except:
            key = None

        # Check if key is 'esc'
        if key == 27:
            quit()

        # Check if key is alphanumeric/punctuation
        elif 32 <= key < 126:
            # TODO - this is the main block of code
            if len(output) < MAX_WIDTH:
                sub_output += chr(key)
            else:
                USER_KEYPRESS.append(chr(key))
                sub_output = chr(key)
                # Check if key is 'delete'
        elif key == 127:
            try:
                USER_KEYPRESS.pop()
            except IndexError:
                continue

        # Check if key is 'enter'
        elif key == 10:
            # TODO - how to declare game over
            quit()

        # Clear window, ready for updated content
        window.clear()

        # Generate output, separating lines so it fits in center

        for index in range(len(PROMPT)):
            sub_output += PROMPT[index]

        # Draw output
        for i in range(len(output)):
            window.addstr(TEXT_START_X + i, TEXT_START_Y, output[i])

        # Display new content
        window.refresh()


if __name__ == "__main__":
    # Sets delay on escape key to 25 milliseconds
    set_shorter_esc_delay_in_os()

    # Calls the main function
    curses.wrapper(main)
