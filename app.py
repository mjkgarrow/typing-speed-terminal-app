import curses
from time import time, sleep
from os import environ, listdir, getcwd
import helpers


def main(window):
    ''' Main app function, a typing speed game'''

    # Calculate window sizes to start game
    window_sizes = helpers.get_window_sizes()
    max_width = window_sizes[0]
    text_start_x = window_sizes[1]
    text_start_y = window_sizes[2]

    # Generate all Curser colours to be used in the app
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i, i, -1)

    # If the scores file doesn't exist, create one
    if "scores.txt" not in listdir(getcwd()):
        with open("scores.txt", "w") as f:
            pass

    # Ask user for menu choice, return a typing prompt
    typing_prompt_wrapped = helpers.menu(window, text_start_x,
                                         text_start_y, max_width)

    # Booleans for checking if game has started and ended
    start = None
    finished_typing = False

    # Boolean for the difficulty setting, False = easy, True = hard
    hard_mode = False

    # Boolean for detect if a user pressed a key
    typed = False

    # Variable to store user input
    user_typed_string = ""

    # Variable to store wpm each time a user types
    # something, used by the consistency function
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
            # Flip difficulty
            hard_mode = not hard_mode
        if helpers.check_esc(key):  # If 'esc', return to menu
            # Clear user typed string
            user_typed_string = ""
            # Reset timer and finished typing
            start = None
            finished_typing = False
            # Return to menu
            typing_prompt_wrapped = helpers.menu(window, text_start_x,
                                                 text_start_y, max_width)
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

        # Map the user input text to the wrapped prompt
        user_typed_wrapped = helpers.wrap_user_input(user_typed_string,
                                                     typing_prompt_wrapped)

        # Boolean variable to see if user has
        # typed the full length of the prompt
        finished_typing = (len(''.join(user_typed_wrapped)) ==
                           len(''.join(typing_prompt_wrapped)))

        # Clear screen so new text can be drawn
        window.erase()

        # Draw directions to screen
        window.addstr(
            0, 0, "Press 'esc' to return to menu - score will not be saved",
            curses.color_pair(39))

        # Display difficulty mode
        if hard_mode:
            window.addstr(
                1, 0, "Difficulty: HARD / No backspaces('tab' to change)",
                curses.color_pair(13))
        else:
            window.addstr(1, 0, "Difficulty: EASY ('tab' to change)",
                          curses.color_pair(39))

        # Show game and stats once user starts typing
        if start != None:
            # Print countdown timer
            countdown = str(30 - (int(time() - start)))
            window.addstr(text_start_y - 3, text_start_x,
                          f"Time remaining: {countdown}",
                          curses.color_pair(208))

            # Calculate wpm and accuracy
            wpm = helpers.calculate_wpm(''.join(typing_prompt_wrapped),
                                        ''.join(user_typed_wrapped),
                                        31 - int(countdown))

            # Store wpm value each time user types a char
            # so consistency value can be computed
            if typed == True:
                wpm_values.append(wpm[1])
                typed = False

            # Calculate consistency
            consistency = helpers.measure_consistency(wpm_values)

            # Print statistics live
            window.addstr(text_start_y - 2, text_start_x,
                          f"Total WPM: {wpm[0]}, Consistency: {consistency}%",
                          curses.color_pair(39))

            # Check if game time is finished or user has finished typing
            if int(countdown) == 0 or finished_typing:
                # Generate final screen with stats
                restart = helpers.final_screen(window, consistency,
                                               wpm[1], wpm[2], hard_mode,
                                               text_start_x, text_start_y)
                if restart == 1:
                    # Clear user typed string
                    user_typed_string = ""
                    # Reset timer and finished typing
                    start = None
                    finished_typing = False
                    # Erase screen
                    window.erase()
                    # Return to menu
                    typing_prompt_wrapped = helpers.menu(
                        window, text_start_x, text_start_y, max_width)
                    continue
        else:
            # Print start game prompt
            window.addstr(text_start_y - 3, text_start_x,
                          f"Start typing to begin the 30 second timer!",
                          curses.color_pair(208))

        # Draw typing test on screen
        helpers.print_typing_text(window, typing_prompt_wrapped,
                                  user_typed_wrapped,
                                  text_start_x, text_start_y)

        # Position cursor at start of typing prompt
        if start == None:
            window.move(text_start_y, text_start_x)

        # Refresh display with new content
        window.refresh()

    helpers.quick_print(window, text_start_x, text_start_y,
                        "Terminal window too small - closing app",
                        curses.color_pair(9))
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
        print("Terminal must be at least 20 lines high and 80 characters wide")
