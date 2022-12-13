import curses
from time import time, sleep
from os import environ, get_terminal_size, listdir, getcwd
from textwrap import wrap
from requests import get
from random import randint
from numpy import mean, var


# Create requirements
# pip freeze > requirements.txt


def check_valid_terminal():
    ''' Checks if valid terminal size'''
    window_size = [get_terminal_size()[0], get_terminal_size()[1]]
    if window_size[0] <= 75 or window_size[1] <= 15:
        return False
    return True


def get_window_sizes():
    ''' Find the size of the terminal window and calculate maximum string width and starting positions'''
    # Get terminal window size [width, height]
    window_size = [get_terminal_size()[0], get_terminal_size()[1]]

    # Calculate max width
    max_width = int(window_size[0]//1.3)

    # Calculate starting positions based on width and window size
    text_start_x = int((window_size[0] - max_width)//2)
    text_start_y = int(window_size[1] * 0.3)
    return [max_width, text_start_x, text_start_y]


def shutdown(window, x, y):
    ''' Displays a goodbye message and quits the program'''
    quick_print(window, x, y, "Goodbye", curses.color_pair(2))
    sleep(1)
    quit()


def load_input_file(window):
    '''Loads prompt txt file from within app directory, returns a string of file contents'''
    window.nodelay(True)
    while True:
        # Get user input (but don't wait for input)
        key = window.getch()

        # If 'enter' key hit then return to main menu
        if key == 10 or key == 13:
            return 0

        # Search through directory to find a file
        for file in listdir(getcwd()):
            if file.endswith(".txt") and (file != "requirements.txt" and file != "scores.txt"):
                with open(file, 'r') as f:
                    lines = f.read().splitlines()
                    return " ".join(lines)


def load_high_score():
    ''' Loads scores file and returns list of scores'''
    file_list = listdir(getcwd())
    if "scores.txt" in file_list:
        with open("scores.txt", 'r') as f:
            return f.read().splitlines()
    return ["No high scores."]


def quick_print(window, x, y, text, colour=None):
    ''' Clears screen and types supplied text with colour option'''
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


def measure_consistency(wpm_values):
    ''' Calculates typing consistency based on the variation of wpm from 0 - 100%'''
    # Calculate the mean of the wpm values
    wpm_mean = mean(wpm_values)

    # Calculate the variance of the wpm values
    wpm_variance = var(wpm_values)

    if wpm_mean == 0 or wpm_variance == 0:
        return 0

    # Calculate the coefficient of variation
    wpm_coefficient = wpm_variance / wpm_mean

    # Map the coefficient of variation onto a scale from 0 to 100
    consistency = 100 - (wpm_coefficient * 100)

    return consistency


def calculate_wpm(prompt, user_typed, time_in_seconds):
    ''' Calculates words-per-minute, accuracy, and consistency'''
    # The function may be called with a user input of 0 characters, so return 0 instead of running the algorithm
    if len(user_typed) == 0:
        return (0, 0, 0)

    # To calculate wpm first the number of mistakes needs to be found
    errors = 0
    for i in range(len(user_typed)):
        if user_typed[i] != prompt[i]:
            errors += 1

    # Gross WPM is how fast you are typing with no error penalties
    gross_wpm = int((len(user_typed)/5)/(time_in_seconds/60))

    # Net WPM uses the Gross WPM and adds an error penalty
    # This means you don't get a high score by just typing nonsense characters
    net_wpm = int(((len(user_typed)/5) - errors)/(time_in_seconds/60))

    # Net WPM can go negative, but wpm only goes to 0
    if net_wpm < 0:
        net_wpm = 0

    # Accuracy is the percentage of correctly typed characters
    accuracy = round(((len(user_typed) - errors)/len(user_typed)) * 100, 1)

    return (gross_wpm, net_wpm, accuracy)


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
            if wrapped_user_typed[line][char] == " ":
                window.addstr(text_start_y + line, text_start_x +
                              char, typing_prompt[line][char], colour)
            else:
                window.addstr(text_start_y + line, text_start_x +
                              char, wrapped_user_typed[line][char], colour)


def sort_scores(scores):
    ''' Sorts scores in descending order by wpm/difficulty/accuracy'''
    # Sort the scores based on accuracy
    scores.sort(key=lambda x: float(
        x.split(": ")[-1].split(", ")[1][:-10]), reverse=True)
    # Sort the scores again based on difficulty (this keeps the original accuracy order if two are the same)
    scores.sort(key=lambda x: x.split(": ")[-1].split(", ")[2])
    # Do a final sort of the scores based on wpm (keeping original order of accuracy and difficulty)
    scores.sort(key=lambda x: int(
        x.split(": ")[-1].split(",")[0][:-3]), reverse=True)
    return scores


def save_score_to_file(username, wpm, accuracy, difficulty):
    ''' Opens or creates a file, sorts the scores by wpm/accuracy/difficulty, saves scores to file'''
    # Check if scores file already exists
    if "scores.txt" in listdir(getcwd()):
        # Open file and read scores into a variable
        with open("scores.txt", "r+") as file_in:
            scores = file_in.readlines()
            # Add the new score to the list of scores
            scores.append(
                f"{username}: {wpm}wpm, {accuracy}% accuracy, {difficulty}")
            # Sort the scores
            sorted_scores = sort_scores(scores)
        # Truncate scores.txt file and re-write sorted scores to it
        with open("scores.txt", "w") as file_out:
            for score in sorted_scores:
                print(score, file=file_out)
        return 1
    # If scores file doesn't exist, create it and add new score
    else:
        with open("scores.txt", "w") as new_file:
            new_file.write(
                f"{username}: {wpm}wpm, {accuracy}% accuracy, {difficulty}")
        return 2


def username_unused(username):
    ''' Checks if submitted username has already been used'''
    if "scores.txt" in listdir(getcwd()):
        # Open file and read scores into a variable
        with open("scores.txt", "r") as file_in:
            names = file_in.readlines()
            for name in names:
                if username == name.split(": ")[0]:
                    return False
            return True
    return True


def save_score_menu(window, wpm, accuracy, difficulty, x, y):
    ''' Displays menu to save score, prevents doubled user names'''
    # Stores username of player
    username = ""

    # Stores difficulty mode
    if difficulty == True:
        difficulty = "Hard mode"
    else:
        difficulty = "Easy mode"

    # Loop to get input
    while True:
        # Get user input
        key = window.getch()

        if 32 <= key < 126:  # Check if key is alphanumeric/punctuation
            # Add to username
            username += chr(key)
        elif key == 127:  # Check if key is backspace
            # Remove from username
            if len(username) > 0:
                username = username[:-1]
        elif key == 10 or key == 13:  # Check if enter key
            # Check username isn't used
            if username_unused(username):
                # Save score to file
                save_score_to_file(username, wpm, accuracy, difficulty)
                return 1
            else:
                # If username used, prompt for new username
                quick_print(
                    window, x, y, f"{username} IS TAKEN, PLEASE CHOOSE A DIFFERENT NAME", curses.color_pair(3))
                sleep(2)
                continue
        elif key == 27:  # Check if key is 'esc', returns to main menu
            return 1

        quick_print(
            window, x, y, f"User name: {username} // Press enter to save")


def final_screen(window, wpm_values, wpm, accuracy, x, y):
    ''' Displays final results of game and asks if you want to save score'''

    # Clear screen
    window.erase()

    while True:

        # Calculate consistency percentage
        consistency = measure_consistency(wpm_values)

        # Print stats
        window.addstr(
            y - 1, x, "Well done! Here are your typing speed stats", curses.color_pair(4))
        statistics = [f"Your words per minute: {wpm}",
                      f"Your accuracy: {accuracy}%",
                      f"Your consistency: {consistency}%",
                      "",
                      "To save score press 's'.",
                      "",
                      "Press 'esc' to quit or 'enter' to return to menu"]
        draw(window, statistics, x, y + 1)

        key = window.getch()

        if key == 27:  # Check if key is 'esc', quits immediately
            shutdown(window, x, y)
        elif key == 115:  # Check if key is 's', return to save file
            return 2
        elif key == 10 or key == 13:  # Check if key is 'enter' return to menu
            return 1


def menu(window, x, y):
    ''' Displays menu for user to select an option, returns a typing prompt based on the option'''
    # Update delay so that program waits on user input
    window.nodelay(False)

    # Set cursor to invisible
    curses.curs_set(0)

    while True:
        menu_text = ["Welcome to Keebz-Typerz, a typing game to test your skills",
                     "Please select an option from the menu:",
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
                    window, x, y, "Please copy a '.txt' file to the app directory to load text")

                # Draw option to return to menu
                window.addstr(
                    0, 0, "Press 'enter' to return to menu", curses.color_pair(2))
                window.refresh()
                # Attempt to load the text file
                file_text = load_input_file(window)

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
                    response = get(
                        "https://www.mit.edu/~ecprice/wordlist.10000").content.splitlines()
                except:
                    # Tell user why request failed
                    quick_print(
                        window, x, y, "Unable to load random words, sorry!", curses.color_pair(3))
                    sleep(2)
                    continue

                # Create a list of 50 random words from response
                word_selection = []
                for i in range(50):
                    word_selection.append(
                        str(response[randint(0, len(response))])[2:-1])

                # Return string of word selection
                return " ".join(word_selection)
            case 51:  # If user presses 3
                # Loading page
                quick_print(
                    window, x, y, "Loading quotes from Type.fit API")
                # Request a wordlist from Quotes API
                try:
                    # Try make request and generate a json from response
                    response = get(
                        "https://type.fit/api/quotes").json()
                except:
                    # Tell user why request failed
                    quick_print(window, x, y, "Unable to load quotes, sorry!")
                    sleep(2)
                    continue

                # Select a random quote from response
                quote = response[randint(0, len(response))]

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
                shutdown(window, x, y)


def main(window):
    ''' Main app function'''
    # Calculate window sizes to start game
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
    typing_prompt = menu(window, text_start_x, text_start_y)

    # Booleans for checking if game has started and ended
    start = None
    finished_typing = False

    # Boolean for the difficulty setting, False = easy, True = hard
    hard_mode = False

    # Boolean for detect if a user pressed a key
    typed = False

    # Variable to store user input
    user_typed_string = ""

    # Variable to store wpm each time a user types something, used by the consistency function
    wpm_values = []

    # Update delay so that program isn't waiting on user input
    window.nodelay(True)

    # Loop to get user input
    while True:

        # Calculate window sizes in while loop so terminal window is adaptive
        window_sizes = get_window_sizes()
        max_width = window_sizes[0]
        text_start_x = window_sizes[1]
        text_start_y = window_sizes[2]

        key = window.getch()
        if key == 27:  # Check if key is 'esc', quits immediately
            shutdown(window, text_start_x, text_start_y)
        elif key == 9:  # Check if key is 'tab', change difficulty mode
            if start != None:
                continue
            else:
                if hard_mode:
                    hard_mode = False
                else:
                    hard_mode = True
        elif key == 10 or key == 13:  # Check if 'enter' key hit, return to menu
            # Clear user typed string
            user_typed_string = ""
            # Reset timer and finished typing
            start = None
            finished_typing = False
            # Return to menu
            typing_prompt = menu(window, text_start_x, text_start_y)
        elif 32 <= key < 126:  # Check if key is alphanumeric/punctuation, add to user input
            # Check if first input, start typing timer
            if len(user_typed_string) == 0:
                # started = True
                start = time()
            user_typed_string += chr(key)
            typed = True
        elif key == 127:  # Check if key is backspace, remove from user input
            if hard_mode:
                continue
            if len(user_typed_string) > 0:
                user_typed_string = user_typed_string[:-1]

        typing_prompt_wrapped = wrap(
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

        # Display difficulty mode
        if hard_mode:
            window.addstr(
                1, 0, "Difficulty: HARD / No backspaces('tab' to change)", curses.color_pair(2))
        else:
            window.addstr(
                1, 0, "Difficulty: EASY ('tab' to change)", curses.color_pair(2))

        # Game mechanics and stats
        if start != None:
            # Print countdown timer
            countdown = str(30 - (int(time() - start)))
            window.addstr(text_start_y - 2, text_start_x,
                          f"Time remaining: {countdown}", curses.color_pair(2))

            # Print WPM
            wpm = calculate_wpm(''.join(typing_prompt_wrapped), ''.join(
                user_typed_wrapped), 31 - int(countdown))
            window.addstr(text_start_y - 1, text_start_x,
                          f"Total WPM: {wpm[0]}, Correct WPM: {wpm[1]}, Accuracy: {wpm[2]}%", curses.color_pair(2))

            # Store wpm value each time user types a char so consistency value can be computed
            if typed == True:
                wpm_values.append(wpm[1])
                typed = False

            # Check if game time is finished or user has finished typing
            if int(countdown) == 0 or finished_typing:
                # Generate final screen with stats
                restart = final_screen(window, wpm_values,
                                       wpm[1], wpm[2], text_start_x, text_start_y)
                if restart == 1:
                    # Clear user typed string
                    user_typed_string = ""
                    # Reset timer and finished typing
                    start = None
                    finished_typing = False
                    # Erase screen
                    window.erase()
                    # Return to menu
                    typing_prompt = menu(window, text_start_x, text_start_y)
                    continue
                elif restart == 2:
                    if save_score_menu(
                            window, wpm[1], wpm[2], hard_mode, text_start_x, text_start_y) == 1:
                        # Clear user typed string
                        user_typed_string = ""
                        # Reset timer and finished typing
                        start = None
                        finished_typing = False
                        # Erase screen
                        window.erase()
                        # Return to menu
                        typing_prompt = menu(
                            window, text_start_x, text_start_y)

        # Draw typing test on screen
        print_typing_text(window, typing_prompt_wrapped, user_typed_wrapped,
                          text_start_x, text_start_y)

        # Display new content
        window.refresh()


if __name__ == "__main__":
    # Sets delay on escape key to 25 milliseconds
    environ.setdefault("ESCDELAY", "25")

    # Checks terminal is a valid size
    if check_valid_terminal():
        # Calls the main function
        curses.wrapper(main)
    else:
        print("Terminal must be at least 20 lines high and 75 characters wide")
