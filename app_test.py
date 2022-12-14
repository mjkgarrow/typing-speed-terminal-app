import app
import unittest.mock
from unittest.mock import patch, mock_open
from unittest import mock
import unittest
import curses


# def test_main(window):
#     pass

class Test_save_score_to_file(unittest.TestCase):
    # Test save_score_to_file is reading and writing to file correctly
    @patch("builtins.open", new_callable=mock_open, read_data="Matt 1: 77wpm, Easy mode, 100.0% accuracy, 84.52% consistency")
    def test_file_read_write(self, mock_file):
        result = app.save_score_to_file(
            'Matt 2', 90, 100.0, 'Easy mode', 84.52)
        self.assertEqual(result, [
            'Matt 2: 90wpm, Easy mode, 100.0% accuracy, 84.52% consistency',
            'Matt 1: 77wpm, Easy mode, 100.0% accuracy, 84.52% consistency'])


class Test_load_high_scores(unittest.TestCase):
    # Test load_high_score is correctly reading the file
    @patch("builtins.open", new_callable=mock_open, read_data="Matt 1: 77wpm, 100.0% accuracy, 84.52% consistency, Easy mode\nMatt 2: 90wpm, Easy mode, 100.0% accuracy, 84.52% consistency")
    def test_file_read(self, mock_file):
        with mock.patch('os.listdir') as mocked_listdir:
            mocked_listdir.return_value = [mock_file]
            result = app.load_high_score()
            self.assertEqual(result, [
                "Matt 1: 77wpm, 100.0% accuracy, 84.52% consistency, Easy mode",
                "Matt 2: 90wpm, Easy mode, 100.0% accuracy, 84.52% consistency"])

    # Test load_high_score is correctly responding to an empty file
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_empty_file(self, mock_file):
        with mock.patch('os.listdir') as mocked_listdir:
            mocked_listdir.return_value = [mock_file]
            result = app.load_high_score()
            self.assertEqual(result, ["No high scores."])


class Test_consistency(unittest.TestCase):
    # Test consistency function with no deviation
    def test_no_std_deviation(self):
        result = app.measure_consistency([65, 65, 65])
        self.assertEqual(result, 100.0)

    # Test consistency function with list of 0s
    def test_zero(self):
        result = app.measure_consistency([0, 0, 0])
        self.assertEqual(result, 0)

    # Test consistency function with only 1 input
    def test_one_input(self):
        result = app.measure_consistency([100])
        self.assertEqual(result, 100.0)

    # Test consistency function with empty list
    def test_empty_list(self):
        result = app.measure_consistency([])
        self.assertEqual(result, 0)


class Test_calculate_wpm(unittest.TestCase):
    # Test wpm calculation with correct user input
    def test_wpm(self):
        prompt = "This is a test case"
        user_typed = "This is a test case"
        time_in_seconds = 60
        result = app.calculate_wpm(
            prompt, user_typed, time_in_seconds)
        self.assertEqual(result, (3, 3, 100.0))

    # Test wpm calculation with correct some input errors
    def test_error_input(self):
        prompt = "This is a test case"
        user_typed = "This is a blur case"
        time_in_seconds = 60
        result = app.calculate_wpm(
            prompt, user_typed, time_in_seconds)
        self.assertEqual(result, (3, 0, 78.9))

    # Test wpm calculation with correct some no input
    def test_no_input(self):
        prompt = "This is a test case"
        user_typed = ""
        time_in_seconds = 60
        result = app.calculate_wpm(
            prompt, user_typed, time_in_seconds)
        self.assertEqual(result, (0, 0, 0))


# class Test_load_input_file(unittest.TestCase):
#     @patch("builtins.open", new_callable=mock_open, read_data="This is a typing prompt")
#     def test_enter_key(self, mock_file):
#         # window = curses.initscr()
#         result = app.load_input_file(self)
#         self.assertEqual(result, ["This is a typing prompt"])

    # def test_enter_key(self):
    #     window = curses.initscr()
    #     result = app.load_input_file(self, window)
    #     self.assertEqual(result)


if __name__ == "__main__":
    unittest.main()
