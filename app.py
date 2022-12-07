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


def check_valid_terminal():
    window_size = [os.get_terminal_size()[0], os.get_terminal_size()[1]]
    if window_size[0] <= 75 or window_size[1] <= 20:
        return False
    else:
        return True


def get_window_sizes():
    # Get terminal window size and calculate the max width of the text, plus the centring coordinates
    window_size = [os.get_terminal_size()[0], os.get_terminal_size()[1]]
    max_width = int(window_size[0]//1.3)
    text_start_x = int((window_size[0] - max_width)//2)
    text_start_y = int(window_size[1] * 0.2)
    return [max_width, text_start_x, text_start_y]


def load_file(window):
    '''Loads prompt txt file from within app directory, returns a string of file contents'''
    window.nodelay(True)
    while True:
        # Get user input (but don't wait for input)
        key = window.getch()

        # If 'enter' key hit then return to main menu
        if key == 10 or key == 13:
            return 0

        # Search through directory to find a file
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


def quick_print(window, x, y, text, colour=None):
    ''' Clears screen and types supplied text'''
    window.erase()
    if colour:
        window.addstr(
            y, x, text, colour)
    else:
        window.addstr(
            y, x, text)
    window.refresh()


def draw(window, text, text_start_x, text_start_y):
    '''Draws list of text to the screen, line by line'''
    for i in range(len(text)):
        window.addstr(text_start_y + i, text_start_x,
                      text[i])


def calculate_wpm(prompt, user, time_in_seconds):
    if len(user) == 0:
        return (0, 0, 0)

    # minutes = time_in_seconds/60
    # gross_wpm = int((user_length/5)/minutes)

    errors = 0
    for i in range(len(user)):
        if user[i] != prompt[i]:
            errors += 1

    # net_wpm = int(gross_wpm - (errors/minutes))
    net_wpm = int(((len(user)/5) - errors)/(time_in_seconds/60))
    accuracy = round(((len(user) - errors)/len(user)) * 100, 1)
    return (net_wpm, accuracy)


def print_typing_text(window, typing_prompt, wrapped_user_typed, text_start_x, text_start_y):
    ''' Draws prompt and user typed input to screen and displays accuracy colour coding '''
    # Draw typing prompt to screen
    draw(window, typing_prompt, text_start_x, text_start_y)

    # Draw user input
    for line in range(len(wrapped_user_typed)):
        for char in range(len(wrapped_user_typed[line])):
            # Change colour of user input text
            if wrapped_user_typed[line][char] != typing_prompt[line][char]:
                colour = curses.color_pair(3)  # Red text if wrong
            else:
                colour = curses.color_pair(2)  # Green text if right
            # Add each individual character to screen
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

        # Display menu options
        for i in range(len(menu_text)):
            if i < 2:
                colour = curses.color_pair(5)  # Magenta title text
            elif i == 6:
                colour = curses.color_pair(3)  # Red quit text
            else:
                colour = curses.color_pair(4)  # Blue option text
            window.addstr(y + i, x, menu_text[i], colour)
        window.refresh()
        key = window.getch()

        match key:
            case 49:  # If user presses 1
                # Tell user to include text-file in app directory
                quick_print(
                    window, x, y, "Copy '.txt' file to app directory to load text")

                # Draw option to return to menu
                window.addstr(
                    0, 0, "Press 'enter' to return to menu", curses.color_pair(2))
                window.refresh()
                # Attempt to load the text file
                file_text = load_file(window)

                # If the file was correctly loaded, return the contents
                if file_text != 0:
                    return file_text
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
                        window, x, y, "Unable to load random words, sorry!", curses.color_pair(3))
                    time.sleep(2)
                    continue

                # Create a list of 50 random words from response
                word_selection = []
                for i in range(50):
                    word_selection.append(
                        str(response[random.randint(0, len(response))])[2:-1])

                # Return string of word selection
                return " ".join(word_selection)
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

                # Return string of quote
                return f"{quote['text']} - {quote['author']}"
            case 52:  # If user presses 4
                # Load high scores file
                scores = load_high_score()
                window.erase()
                window.addstr(
                    0, 0, "Press 'esc' to exit, 'enter' to return to menu", curses.color_pair(2))
                # Print scores to screen
                draw(window, scores, x, y)
                window.refresh()
                # Wait for user input
                window.getch()
            case 53:  # If user presses 5
                # Print goodbye message
                quick_print(
                    window, x, y, "Goodbye", curses.color_pair(2))
                # Wait a second and quit
                time.sleep(1)
                quit()


def main(window):

    window_sizes = get_window_sizes()
    max_width = window_sizes[0]
    text_start_x = window_sizes[1]
    text_start_y = window_sizes[2]

    # Applying text styling colours to the curses class
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # white text
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # green text
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)  # red text
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)  # blue text
    curses.init_pair(5, curses.COLOR_MAGENTA,
                     curses.COLOR_BLACK)  # magenta text

    # Ask user for menu choice, return a typing prompt
    typing_prompt = menu(window, text_start_x, text_start_y, max_width)

    # Update delay so that program isn't waiting on user input
    window.nodelay(True)

    # Boolean for checking if game has started and ended
    started = False
    finished_typing = False

    # Boolean for the difficulty setting, False = easy, True = hard
    hard_mode = False

    # Variable to store user input
    user_typed_string = ""
    while True:

        window_sizes = get_window_sizes()
        max_width = window_sizes[0]
        text_start_x = window_sizes[1]
        text_start_y = window_sizes[2]

        key = window.getch()
        if key == 27:  # Check if key is 'esc', quits immediately
            quick_print(window, text_start_x, text_start_y,
                        "Goodbye", curses.color_pair(2))
            time.sleep(1)
            quit()
        elif key == 9:  # Check if key is 'tab', change hard mode
            if started:
                continue
            else:
                if hard_mode:
                    hard_mode = False
                else:
                    hard_mode = True
        elif key == 10 or key == 13:  # Check if 'enter' key hit, clears input and returns to main menu
            user_typed_string = ""
            typing_prompt = menu(window, text_start_x, text_start_y, max_width)
        elif 32 <= key < 126:  # Check if key is alphanumeric/punctuation, add to user input
            # Check if first input, start typing timer
            if len(user_typed_string) == 0:
                started = True
                start = time.time()
            user_typed_string += chr(key)
        elif key == 127:  # Check if key is backspace, remove from user input
            if len(user_typed_string) > 0:
                user_typed_string = user_typed_string[:-1]

        typing_prompt_wrapped = textwrap.wrap(
            typing_prompt, max_width, drop_whitespace=False)

        # Creates a list of sub-strings from the user input string so it can be correctly displayed over the top of the prompt.
        sub_numbers = [len(i) for i in typing_prompt_wrapped]
        user_typed_wrapped = [user_typed_string[sum(
            sub_numbers[:i]):sum(sub_numbers[:i+1])] for i in range(len(sub_numbers))]

        # Algorithm to see if user has finished typing
        prompt_length = len(''.join(typing_prompt_wrapped))
        user_typed_length = len(''.join(user_typed_wrapped))

        if prompt_length == user_typed_length:
            finished_typing = True

        # Clear screen so new text can be drawn
        window.erase()

        # Draw directions to screen
        window.addstr(
            0, 0, "Press 'esc' to exit, 'enter' to return to menu - score will not be saved", curses.color_pair(2))
        window.addstr(
            1, 0, "For hard mode press 'tab'", curses.color_pair(2))

        if hard_mode:
            window.clrtoeol()
            window.addstr(
                1, 0, "Difficulty: HARD (press 'tab' to return to easy mode)", curses.color_pair(2))

        # Game time mechanic
        if started:
            # TODO print countdown, print wpm, print accuracy
            # Print countdown timer
            countdown = str(60 - (int(time.time() - start)))
            window.addstr(text_start_y - 2, text_start_x,
                          f"Time remaining - {countdown}", curses.color_pair(2))

            # Print WPM
            wpm = calculate_wpm(''.join(typing_prompt_wrapped), ''.join(
                user_typed_wrapped), 61 - int(countdown))
            window.addstr(text_start_y - 1, text_start_x,
                          f"WPM: {wpm[0]}, Accuracy: {wpm[1]}%", curses.color_pair(2))
            # Check if game time is finished or user has finished typing
            if int(countdown) <= 0 or finished_typing:
                # TODO go to finished screen
                quit()

        print_typing_text(window, typing_prompt_wrapped, user_typed_wrapped,
                          text_start_x, text_start_y)

        # Display new content
        window.refresh()


if __name__ == "__main__":
    # Sets delay on escape key to 25 milliseconds
    os.environ.setdefault("ESCDELAY", "25")

    if check_valid_terminal():
        # Calls the main function
        curses.wrapper(main)
    else:
        print("Terminal must be at least 20 lines high and 75 characters wide")
