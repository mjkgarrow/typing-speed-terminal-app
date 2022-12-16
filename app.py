import curses
from time import time, sleep
from os import environ, listdir, getcwd
from textwrap import wrap
import helpers


def main(window):
    ''' Main app function, a typing speed game'''

    # Calculate window sizes to start game
    window_sizes = helpers.get_window_sizes()
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

    # If the scores file doesn't exist, create one
    if 'scores.txt' not in listdir(getcwd()):
        with open('scores.txt', 'w') as f:
            pass

    # Ask user for menu choice, return a typing prompt
    typing_prompt = helpers.menu(window, text_start_x, text_start_y)

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

    # Loop to get user input
    while helpers.check_valid_terminal():

        # Set cursor visibility so user can see where they are typing
        curses.curs_set(1)

        # Update delay so that program isn't waiting on user input
        window.nodelay(True)

        # Calculate window sizes in while loop so terminal window is adaptive
        window_sizes = helpers.get_window_sizes()
        max_width = window_sizes[0]
        text_start_x = window_sizes[1]
        text_start_y = window_sizes[2]

        # Get user input
        key = window.getch()

        # Check user input
        if key == 9:  # If 'tab', change difficulty mode
            if start != None:
                continue
            if hard_mode:
                hard_mode = False
            else:
                hard_mode = True
        if helpers.check_esc(key):  # If 'esc', return to menu
            # Clear user typed string
            user_typed_string = ""
            # Reset timer and finished typing
            start = None
            finished_typing = False
            # Return to menu
            typing_prompt = helpers.menu(window, text_start_x, text_start_y)
            continue
        elif helpers.check_ascii_input(key):  # If key ascii
            # Check if first input, start typing timer
            if len(user_typed_string) == 0:
                # started = True
                start = time()
            user_typed_string += chr(key)
            typed = True
        elif helpers.check_backspace(key):  # If 'backspace', delete
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
            0, 0, "Press 'esc' to return to menu - score will not be saved", curses.color_pair(4))

        # Display difficulty mode
        if hard_mode:
            window.addstr(
                1, 0, "Difficulty: HARD / No backspaces('tab' to change)", curses.color_pair(5))
        else:
            window.addstr(
                1, 0, "Difficulty: EASY ('tab' to change)", curses.color_pair(4))

        # Show game and stats once user starts typing
        if start != None:
            # Print countdown timer
            countdown = str(30 - (int(time() - start)))
            window.addstr(text_start_y - 2, text_start_x,
                          f"Time remaining: {countdown}", curses.color_pair(3))

            # Calculate wpm and accuracy
            wpm = helpers.calculate_wpm(''.join(typing_prompt_wrapped), ''.join(
                user_typed_wrapped), 31 - int(countdown))

            # Store wpm value each time user types a char so consistency value can be computed
            if typed == True:
                wpm_values.append(wpm[1])
                typed = False

            # Calculate consistency
            consistency = helpers.measure_consistency(wpm_values)

            # Print statistics live
            window.addstr(text_start_y - 1, text_start_x,
                          f"Total WPM: {wpm[0]}, Correct WPM: {wpm[1]}, Accuracy: {wpm[2]}%, Consistency: {consistency}", curses.color_pair(4))

            # Check if game time is finished or user has finished typing
            if int(countdown) == 0 or finished_typing:
                # Generate final screen with stats
                restart = helpers.final_screen(window, consistency,
                                               wpm[1], wpm[2], hard_mode, text_start_x, text_start_y)
                if restart == 1:
                    # Clear user typed string
                    user_typed_string = ""
                    # Reset timer and finished typing
                    start = None
                    finished_typing = False
                    # Erase screen
                    window.erase()
                    # Return to menu
                    typing_prompt = helpers.menu(
                        window, text_start_x, text_start_y)
                    continue
                elif restart == None:
                    helpers.quick_print(
                        window, text_start_x, text_start_y, "Please provide a valid file path...", curses.color_pair(3))
                    sleep(1)
                    window.erase()

        # Draw typing test on screen
        helpers.print_typing_text(window, typing_prompt_wrapped, user_typed_wrapped,
                                  text_start_x, text_start_y)

        # Position cursor at start of typing prompt
        if start == None:
            window.move(text_start_y, text_start_x)

        # Refresh display with new content
        window.refresh()

    helpers.quick_print(window, text_start_x, text_start_y,
                        "Terminal window too small - closing app", curses.color_pair(3))
    sleep(2)
    quit()


if __name__ == "__main__":
    # Sets delay on escape key to 25 milliseconds
    environ.setdefault("ESCDELAY", "25")

    # Checks terminal is a valid size
    if helpers.check_valid_terminal():
        # Calls the main function
        curses.wrapper(main)
    else:
        print("Terminal must be at least 20 lines high and 75 characters wide")
