import curses
import time
import os
import textwrap
import requests
import random


# Create requirements
# pip freeze > requirements.txt

# Working folder director
DIRECTORY = os.getcwd()


def load_file(window):
    '''Loads prompt txt file from within app directory, returns a string of file contents'''
    while True:
        key = window.getch()
        # Check if 'enter' key hit returns to main menu
        if key == 10 or key == 13:
            return 0
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


def draw(window, text, text_start_x, text_start_y):
    '''Draws list of text to the screen, line by line'''
    for i in range(len(text)):
        window.addstr(text_start_y + i, text_start_x,
                      text[i])


def calculate_wpm(wrapped_user_typed):
    pass


def print_screen(window, typing_prompt, wrapped_user_typed, text_start_x, text_start_y):

    # Draw typing prompt to screen
    draw(window, typing_prompt, text_start_x, text_start_y)

    # Draw user input
    for line in range(len(wrapped_user_typed)):
        for char in range(len(wrapped_user_typed[line])):
            colour = curses.color_pair(2)
            if wrapped_user_typed[line][char] != typing_prompt[line][char]:
                colour = curses.color_pair(3)
            window.addstr(text_start_y + line, text_start_x + char,
                          wrapped_user_typed[line][char], colour)


def menu(window, x, y, max_width):
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
            case 49:  # If user presses '1'
                # Tell user to include text-file in app directory
                quick_print(
                    window, x, y, "Copy '.txt' file to app directory to load text")
                window.addstr(
                    0, 0, "Press 'enter' to return to menu")
                window.refresh()
                file_text = load_file(window)
                if file_text != 0:
                    return textwrap.wrap(file_text, max_width)
            case 50:  # If user presses 2
                # Loading page
                quick_print(
                    window, x, y, "Loading words from MIT")
                # Request a wordlist from MIT API
                try:
                    # Try make request and generate list of all words from the response
                    response = requests.get(
                        "https://www.mit.edu/~ecprice/wordlist.10000").content.splitlines()
                except:
                    # Tell user why request failed
                    quick_print(
                        window, x, y, "Unable to load random words, sorry!")
                    time.sleep(2)
                    continue

                # Create a list of 50 random words from response
                word_selection = []
                for i in range(50):
                    word_selection.append(
                        str(response[random.randint(0, len(response))])[2:-1])

                # Return a list of strings that are wrapped to the length of the terminal
                return textwrap.wrap(" ".join(word_selection), max_width)
            case 51:  # If user presses 3
                # Loading page
                quick_print(
                    window, x, y, "Loading quotes from Type.fit API")
                # Request a wordlist from Quotes API
                try:
                    # Try make request and generate a json from response
                    response = requests.get(
                        "https://type.fit/api/quotes").json()
                except:
                    # Tell user why request failed
                    quick_print(window, x, y, "Unable to load quotes, sorry!")
                    time.sleep(2)
                    continue

                # Select a random quote from response
                quote = response[random.randint(0, len(response))]

                # Return a list of strings that are wrapped to the length of the terminal
                return textwrap.wrap(f"{quote['text']} - {quote['author']}", max_width)
            case 52:  # If user presses 4
                scores = load_high_score()
                window.erase()
                window.addstr(
                    0, 0, "Press 'esc' to exit, 'enter' to return to menu")
                draw(window, scores, x, y)
                window.refresh()
                window.getch()
            case 53:  # If user presses 5
                quick_print(
                    window, x, y, "Goodbye")
                time.sleep(1)
                quit()

        window.refresh()


def main(window):
    # Get terminal window size and calculate the max width of the text, plus the centering coordinates
    window_size = [os.get_terminal_size()[0], os.get_terminal_size()[1]]
    max_width = int(window_size[0]//1.3)
    text_start_x = int((window_size[0] - max_width)//2)
    text_start_y = int(window_size[1] * 0.2)

    # Applying text styling colours to the curses class
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # white text
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # green text
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)  # red text
    white = curses.color_pair(1)
    green = curses.color_pair(2)
    red = curses.color_pair(3)

    # Ask user for menu choice, return a typing prompt
    typing_prompt = menu(window, text_start_x, text_start_y,
                         max_width)

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
            quick_print(window, text_start_x, text_start_y, "Goodbye")
            time.sleep(1)
            quit()
        # Check if 'enter' key hit, clears input and returns to main menu
        if key == 10 or key == 13:
            user_typed_string = ""
            typing_prompt = menu(window, text_start_x, text_start_y, max_width)
        # Check if key is alphanumeric/punctuation, add to user input
        elif 32 <= key < 126:
            user_typed_string += chr(key)
        # Check if key is backspace, remove from user input
        elif key == 127:
            if len(user_typed_string) > 0:
                user_typed_string = user_typed_string[:-1]

        # Creates a list of sub-strings from the user input string so it can be displayed over the top of the prompt.
        n = [len(i) for i in typing_prompt]
        wrapped_user_typed = [user_typed_string[sum(
            n[:i]):sum(n[:i+1])] for i in range(len(n))]

        # Clear screen so new text can be drawn
        window.erase()

        # Draw menu directions to screen
        window.addstr(0, 0, "Press 'esc' to exit, 'enter' to return to menu")

        print_screen(window, typing_prompt, wrapped_user_typed,
                     text_start_x, text_start_y)

        # Display new content
        window.refresh()


if __name__ == "__main__":
    # Sets delay on escape key to 25 milliseconds
    os.environ.setdefault("ESCDELAY", "25")

    # Calls the main function
    curses.wrapper(main)
