import curses
from time import time, sleep
from os import environ, get_terminal_size, listdir, getcwd
from textwrap import wrap
from requests import get
from random import randint
from numpy import mean, std


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


def load_input_file():
    '''Loads prompt txt file from within app directory, returns a string of file contents'''
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
            results = f.read().splitlines()
            if len(results) == 0:
                return ["No high scores."]
            return results
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


# Tested in pytest
def measure_consistency(wpm_values):
    ''' Calculates typing consistency based on the variation of wpm from 0 - 100%
        Algorithm from https://monkeytype.com/about'''
    # If provided an empty wpm_values list, return 0
    if len(wpm_values) == 0:
        return round(0, 2)

    # Calculate the mean of the wpm values
    wpm_mean = mean(wpm_values)

    if wpm_mean == 0:
        return round(0, 2)

    # Calculate the standard deviation of the wpm values
    wpm_standard_deviation = std(wpm_values)

    # Calculate the coefficient of variation
    wpm_coefficient = wpm_standard_deviation / wpm_mean

    # Map the coefficient of variation onto a scale from 0 to 100
    consistency = 100 - (wpm_coefficient * 100)

    if consistency < 0:
        return round(0, 2)

    return round(consistency, 2)


# Tested in pytest
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


# Tested in pytest
def sort_scores(scores):
    ''' Sorts scores in descending order by wpm/difficulty/accuracy'''
    # Loop over scores to separate values so they can be sorted
    score_list = []
    for score in scores:
        # Split scores up into name and results, then append to score_list
        name = score.split(": ")[0]
        results = score.split(": ")[-1].split(", ")
        score_list.append([name, *results])

    # Sort the new list of values
    score_list.sort(key=lambda x: (x[1][:-3], x[2], x[3][:-10]), reverse=True)

    # Recombine the list of lists back into a list of strings
    for i in range(len(score_list)):
        score_list[i] = f"{score_list[i][0]}: {score_list[i][1]}, {score_list[i][2]}, {score_list[i][3]}, {score_list[i][4]}"
    return score_list


# Tested in pytest
def save_score_to_file(username, wpm, accuracy, difficulty, consistency):
    ''' Opens or creates a file, sorts the scores by wpm/accuracy/difficulty, saves scores to file'''
    # Check if scores file already exists
    if "scores.txt" in listdir(getcwd()):
        # Open file and read scores into a variable
        with open("scores.txt", "r+") as file_in:
            scores = file_in.read().splitlines()
            # Add the new score to the list of scores
            # scores.append(
            #     f"{username}: {wpm}wpm, {accuracy}% accuracy, {consistency}% consistency, {difficulty}")
            scores.append(
                f"{username}: {wpm}wpm, {difficulty}, {accuracy}% accuracy, {consistency}% consistency")
            # Sort the scores
            sorted_scores = sort_scores(scores)
        # Truncate scores.txt file and re-write sorted scores to it
        with open("scores.txt", "w") as file_out:
            for score in sorted_scores:
                print(score, file=file_out)
        # Return sorted score list for testing purposes
        return sorted_scores
    # If scores file doesn't exist, create it and add new score
    else:
        with open("scores.txt", "w") as new_file:
            new_file.write(
                f"{username}: {wpm}wpm, {difficulty}, {accuracy}% accuracy, {consistency}% consistency")
        # Return score for testing purposes
        return [f"{username}: {wpm}wpm, {difficulty}, {accuracy}% accuracy, {consistency}% consistency"]


# Tested in pytest
def username_unused(username):
    ''' Checks if submitted username has already been used'''
    if username == "":
        return False
    if "scores.txt" in listdir(getcwd()):
        # Open file and read scores into a variable
        with open("scores.txt", "r") as file_in:
            lines = file_in.readlines()
            for name in lines:
                if username == name.split(": ")[0]:
                    return False
            return True
    return True


def final_screen(window, consistency, wpm, accuracy, difficulty, x, y):
    ''' Displays final results of game and asks if you want to save score'''

    # Clear screen
    window.erase()

    # Stores username of player
    username = ""

    # Stores difficulty mode
    if difficulty == True:
        difficulty = "Hard mode"
    else:
        difficulty = "Easy mode"

    # Loop to get user input
    while True:
        # Print congratulations
        window.addstr(
            y - 1, x, "Well done! Here are your typing speed stats", curses.color_pair(4))

        # List of statistics
        statistics = [f"Your words per minute: {wpm}",
                      f"Your accuracy: {accuracy}%",
                      f"Your consistency: {consistency}%",
                      "",
                      f"Type username to save score: {username} ",
                      "",
                      "Press 'enter' to save or 'esc' to return to menu"]

        # Draw statistics on screen
        draw(window, statistics, x, y + 1)

        # Position cursor to username typing area
        window.move(y + 5, x + (len(statistics[4]) - 1))

        # Refresh window with text
        window.refresh()

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
            if username_unused(username.strip()):
                # Save score to file
                save_score_to_file(username.strip(), wpm, accuracy,
                                   difficulty, consistency)
                return 1
            else:
                # If username used, prompt for new username
                window.addstr(
                    y + 5, x, "CAN'T USE THAT NAME, PLEASE CHOOSE A DIFFERENT NAME", curses.color_pair(3))
                window.refresh()
                sleep(2)
                window.erase()
                username = ""
        elif key == 27:  # Check if key is 'esc', returns to main menu
            return 1


# Tested in pytest
def load_api(url):
    # Request responses from API
    try:
        # Try make request and generate list of all words from the response
        if "quotes" in url:
            response = get("https://type.fit/api/quotes", timeout=2).json()
        else:
            response = get("https://www.mit.edu/~ecprice/wordlist.10000",
                           timeout=2).content.splitlines()
    except:
        return 0
    if "quotes" in url:
        # Select a random quote from response
        quote = response[randint(0, len(response))]

        # Return string of quote
        return f"{quote['text']} - {quote['author']}"
    else:
        # Create a list of 50 random words from response
        word_selection = [response[randint(0, len(response))].decode(
            encoding='UTF-8') for _ in range(50)]

        # Return string of word selection
        return " ".join(word_selection)


def menu(window, x, y):
    ''' Displays menu for user to select an option, returns a typing prompt based on the option'''

    # Set cursor to invisible
    curses.curs_set(0)

    # Update delay so that program waits on user input
    window.nodelay(False)

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
                # Set input delay to True so program waits for input
                window.nodelay(True)
                #
                # quick_print(
                #     window, x, y, "Please copy a '.txt' file to the app directory to load text")
                window.erase()
                # Draw option to return to menu and ell user to include text-file in app directory
                window.addstr(
                    0, 0, "Press 'enter' to return to menu", curses.color_pair(2))
                window.addstr(
                    y, x, "Please copy a '.txt' file to the app directory to load text")
                window.refresh()
                # Attempt to load the text file
                while True:
                    key = window.getch()

                    file_text = load_input_file()

                    if key == 10 or key == 13:
                        file_text = 0
                        break
                    elif (type(file_text) == str):
                        break

                # If the file was correctly loaded, return the contents
                if file_text != 0:
                    return file_text
            case 50:  # If user presses 2
                # Loading page
                quick_print(
                    window, x, y, "Loading words from MIT")

                # Make API call
                response = load_api(
                    "https://www.mit.edu/~ecprice/wordlist.10000")

                # Check if response is correct
                if response != 0:
                    return response
                else:
                    # Tell user why request failed
                    quick_print(
                        window, x, y, "Unable to load random words, sorry!", curses.color_pair(3))
                    sleep(2)
                    continue
            case 51:  # If user presses 3
                # Display loading screen
                quick_print(
                    window, x, y, "Loading words from MIT")

                # Make API call
                response = load_api("https://type.fit/api/quotes")
                # Check if response is correct
                if response != 0:
                    return response
                else:
                    # Tell user why request failed
                    quick_print(
                        window, x, y, "Unable to load random words, sorry!", curses.color_pair(3))
                    sleep(2)
                    continue
            case 52:  # If user presses 4
                # Load high scores file
                scores = load_high_score()
                window.erase()
                window.addstr(
                    0, 0, "Press any key to return to menu", curses.color_pair(2))
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

    # Set cursor visibility so user can see where they are typing
    curses.curs_set(1)

    # Loop to get user input
    while True:

        # Update delay so that program isn't waiting on user input
        window.nodelay(True)

        # Calculate window sizes in while loop so terminal window is adaptive
        window_sizes = get_window_sizes()
        max_width = window_sizes[0]
        text_start_x = window_sizes[1]
        text_start_y = window_sizes[2]

        # Get user input
        key = window.getch()
        if key == 27:  # Check if key is 'esc', quits immediately
            shutdown(window, text_start_x, text_start_y)
        elif key == 9:  # Check if key is 'tab', change difficulty mode
            if start != None:
                continue
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
            continue
        elif 32 <= key < 126:  # Check if key is alphanumeric/punctuation, add to user input
            # Check if first input, start typing timer
            if len(user_typed_string) == 0:
                # started = True
                start = time()
            user_typed_string += chr(key)
            typed = True
        elif key == 127:  # Check if key is backspace, remove from user input
            # Hard mode prevents user from using backspace
            if hard_mode:
                continue
            if len(user_typed_string) > 0:
                user_typed_string = user_typed_string[:-1]

        # Wrap typing prompt so it fits in terminal window
        typing_prompt_wrapped = wrap(
            typing_prompt, max_width, drop_whitespace=False)

        # Creates a list of sub-strings from the user input string so it can be correctly displayed over the top of the prompt.
        sub_numbers = [len(i) for i in typing_prompt_wrapped]
        user_typed_wrapped = [user_typed_string[sum(
            sub_numbers[:i]):sum(sub_numbers[:i+1])] for i in range(len(sub_numbers))]

        # See if user has typed the full length of the prompt
        if len(''.join(user_typed_wrapped)) == len(''.join(typing_prompt_wrapped)):
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

        # Show game and stats once user starts typing
        if start != None:
            # Print countdown timer
            countdown = str(30 - (int(time() - start)))
            window.addstr(text_start_y - 2, text_start_x,
                          f"Time remaining: {countdown}", curses.color_pair(3))

            # Calculate wpm and accuracy
            wpm = calculate_wpm(''.join(typing_prompt_wrapped), ''.join(
                user_typed_wrapped), 31 - int(countdown))

            # Store wpm value each time user types a char so consistency value can be computed
            if typed == True:
                wpm_values.append(wpm[1])
                typed = False

            # Calculate consistency
            consistency = measure_consistency(wpm_values)

            # Print statistics live
            window.addstr(text_start_y - 1, text_start_x,
                          f"Total WPM: {wpm[0]}, Correct WPM: {wpm[1]}, Accuracy: {wpm[2]}%, Consistency: {consistency}", curses.color_pair(4))

            # Check if game time is finished or user has finished typing
            if int(countdown) == 0 or finished_typing:
                # Generate final screen with stats
                restart = final_screen(window, consistency,
                                       wpm[1], wpm[2], hard_mode, text_start_x, text_start_y)
                if restart:
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

        # Draw typing test on screen
        print_typing_text(window, typing_prompt_wrapped, user_typed_wrapped,
                          text_start_x, text_start_y)

        # Position cursor at start of typing prompt
        if start == None:
            window.move(text_start_y, text_start_x)

        # Refresh display with new content
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
