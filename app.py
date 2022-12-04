import curses
import time
import os


USER_KEYPRESS = []
PROMPT = []


def set_shorter_esc_delay_in_os():
    '''Triggers escape key immediately rather than waiting a second'''
    os.environ.setdefault('ESCDELAY', '25')


def main(window):

    window_size = [os.get_terminal_size()[0], os.get_terminal_size()[1]]
    max_width = int(window_size[0]//1.3)
    text_start = int((window_size[0] - max_width)//2)

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    WHITE_COLOUR = curses.color_pair(1)
    GREEN_COLOUR = curses.color_pair(2)
    RED_COLOUR = curses.color_pair(3)

    while True:
        # Get the inputted key from user
        key = window.getch()

        # Check if key is 'esc'
        if key == 27:
            quit()

        # Check if key is alphanumeric/punctuation
        elif 32 <= key < 126:
            # TODO - this is the main block of code
            USER_KEYPRESS.append(chr(key))

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

        window.clear()

        # Generate output onto screen, separating lines so it fits in center
        output = [str(max_width), 1]
        sub_output = ''
        for index in range(len(USER_KEYPRESS)):
            sub_output += str(index)
            # if index % max_width != 0:
            #     sub_output += USER_KEYPRESS[index]
            # else:
            #     sub_output += USER_KEYPRESS[index]
            #     output.append(sub_output)
            #     sub_output = ''

        # Draw output
        # window.addstr(0, text_start, output[0])
        for i in range(len(output)):
            window.addstr(i, text_start, output[0])

        # Display new content
        window.refresh()


if __name__ == '__main__':
    # Sets delay on escape key to 25 milliseconds
    set_shorter_esc_delay_in_os()

    # Calls the main function
    curses.wrapper(main)
