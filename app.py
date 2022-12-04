import curses
import time
import os


def main(window):

    while True:
        # Get the inputted key from user
        key = window.getch()

        # Check if key is 'esc'
        if key == 27:
            quit()

        # Check if key is alphanumeric/punctuation
        elif 32 < key < 126:
            # TODO - this is the main block of code
            window.addstr(chr(key))
            pass

        # Check if key is 'delete'
        elif key == 127:
            # TODO - how to delete
            pass

        # Check if key is 'enter'
        elif key == 13:
            # TODO - how to declare game over
            pass

        # Display new content
        window.refresh()


if __name__ == '__main__':
    # Calls the main function
    curses.wrapper(main)
