import curses
import time
import os
import textwrap
import requests
import random

MENU_OPTION = 0
USER_KEYPRESS = ""
PROMPT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent tempor nulla id finibus maximus. Sed eget efficitur dolor, in sodales massa. Donec vitae condimentum lectus, ut scelerisque ex. Vivamus aliquet aliquam diam eu hendrerit. Donec et mauris non arcu aliquet elementum. Aliquam ultrices ac sem non ornare. Donec bibendum pharetra lorem, ut ullamcorper nisi rhoncus at. In eu lacus non tortor interdum varius. Suspendisse aliquam ex eu dignissim dictum. Morbi non cursus dui. Praesent auctor nisi vitae est iaculis tempus. Aliquam scelerisque convallis lorem ut aliquam. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae."


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
    file_path = ""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return f.read().splitlines()
    else:
        return 1


def quick_print(window, x, y, text):
    window.clear()
    window.addstr(
        y, x, text)
    window.refresh()


def menu(window, x, y):
    while True:
        menu_text = ["Welcome to Speed-Typer, an typing game to test your skills",
                     "Please select from the following options:",
                     "1. Test from file",
                     "2. Test random words",
                     "3. Test a quote",
                     "5. Quit"]

        key = window.getch()

        for i in range(len(menu_text)):
            window.addstr(y + i, x, menu_text[i])

        window.refresh()

        match key:
            case 27:
                quit()
            case 49:
                quick_print(
                    window, x, y, "To load file, drag file to 'in-file folder")
                file_text = load_file(window)
                if file_text != 1:
                    return file_text
            case 50:
                try:
                    response = requests.get(
                        "https://www.mit.edu/~ecprice/wordlist.10000")
                WORDS = response.content.splitlines()
                word_selection = []
                for i in range(200):
                    word_selection.append(WORDS[random.random(0, len(WORDS))])
                return word_selection


def main(window):
    window.nodelay(True)

    # Finding the terminal window size to correctly center text
    window_size = [os.get_terminal_size()[0], os.get_terminal_size()[1]]
    max_width = int(window_size[0]//1.3)
    text_start_x = int((window_size[0] - max_width)//2)
    text_start_y = int(window_size[1] * 0.2)

    # Applying text styling colours to variables
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    white = curses.color_pair(1)
    green = curses.color_pair(2)
    red = curses.color_pair(3)

    response = menu(window, text_start_x, text_start_y)

    output = []
    sub_output = ''
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
            if len(output) < max_width:
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
            window.addstr(text_start_x + i, text_start_y, output[i])

        # Display new content
        window.refresh()


if __name__ == "__main__":
    # Sets delay on escape key to 25 milliseconds
    set_shorter_esc_delay_in_os()

    # Calls the main function
    curses.wrapper(main)
