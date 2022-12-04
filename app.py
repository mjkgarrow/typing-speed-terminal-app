import curses
import time
import os


def main(window):

    while True:
        # Get the inputted key from user
        key = window.getkey()

        # Check if key is 'esc'
        if key == '^[':
            quit()

        # Check if key is alphanumeric/punctuation
        elif 32 < ord(key) < 126:
            # TODO - this is the main block of code
            pass

        # Check if key is 'delete'
        elif key == 'KEY_BACKSPACE':
            # TODO - how to delete
            pass

        # Check if key is 'enter'
        elif key == 'KEY_ENTER':
            # TODO - how to declare game over
            pass


if __name__ == '__main__':
    # Calls the main function
    curses.wrapper(main)
