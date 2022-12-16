import helpers
import helpers
import unittest
from unittest import mock
from unittest.mock import patch, mock_open


class Test_save_score_to_file(unittest.TestCase):
    @ patch("builtins.open", new_callable=mock_open, read_data="Matt 1: 77wpm, Easy mode, 100.0% accuracy, 84.52% consistency")
    def test_file_read_write(self, mock_file):
        result = helpers.save_score_to_file(
            'Matt 2', 90, 100.0, 'Easy mode', 84.52)
        assert result == [
            'Matt 2: 90wpm, Easy mode, 100.0% accuracy, 84.52% consistency'] or result == [
            'Matt 2: 90wpm, Easy mode, 100.0% accuracy, 84.52% consistency',
            'Matt 1: 77wpm, Easy mode, 100.0% accuracy, 84.52% consistency']


class Test_load_high_scores(unittest.TestCase):
    # Test load_high_score is correctly reading the file
    @ patch("builtins.open", new_callable=mock_open, read_data="Matt 1: 77wpm, 100.0% accuracy, 84.52% consistency, Easy mode\nMatt 2: 90wpm, Easy mode, 100.0% accuracy, 84.52% consistency")
    def test_file_read(self, mock_file):
        with mock.patch('os.listdir') as mocked_listdir:
            mocked_listdir.return_value = [mock_file]
            result = helpers.load_high_score()
            assert result == [
                "Matt 1: 77wpm, 100.0% accuracy, 84.52% consistency, Easy mode", "Matt 2: 90wpm, Easy mode, 100.0% accuracy, 84.52% consistency"]

    # Test load_high_score is correctly responding to an empty file
    @ patch("builtins.open", new_callable=mock_open, read_data="")
    def test_empty_file(self, mock_file):
        with mock.patch('os.listdir') as mocked_listdir:
            mocked_listdir.return_value = [mock_file]
            result = helpers.load_high_score()
            assert result == ["No high scores."]

    # Test load_high_score is correctly responding to an empty file
    @ patch("builtins.open", new_callable=mock_open, read_data="sauhidfkashfkasdlkjrh iusaheflkasbdflkjas baksjdf")
    def test_bad_file(self, mock_file):
        with mock.patch('os.listdir') as mocked_listdir:
            mocked_listdir.return_value = [mock_file]
            result = helpers.load_high_score()
            assert result == None


class Test_consistency(unittest.TestCase):
    # Test consistency function with no deviation
    def test_no_std_deviation(self):
        result = helpers.measure_consistency([65, 65, 65])
        self.assertEqual(result, 100.0)

    # Test consistency function with list of 0s
    def test_zero(self):
        result = helpers.measure_consistency([0, 0, 0])
        self.assertEqual(result, 0)

    # Test consistency function with only 1 input
    def test_one_input(self):
        result = helpers.measure_consistency([100])
        self.assertEqual(result, 100.0)

    # Test consistency function with empty list
    def test_empty_list(self):
        result = helpers.measure_consistency([])
        self.assertEqual(result, 0)


class Test_calculate_wpm(unittest.TestCase):
    # Test wpm calculation with correct user input
    def test_wpm(self):
        prompt = "This is a test case"
        user_typed = "This is a test case"
        time_in_seconds = 60
        result = helpers.calculate_wpm(
            prompt, user_typed, time_in_seconds)
        self.assertEqual(result, (3, 3, 100.0))

    # Test wpm calculation with correct some input errors
    def test_error_input(self):
        prompt = "This is a test case"
        user_typed = "This is a blur case"
        time_in_seconds = 60
        result = helpers.calculate_wpm(
            prompt, user_typed, time_in_seconds)
        self.assertEqual(result, (3, 0, 78.9))

    # Test wpm calculation with correct no input
    def test_no_input(self):
        prompt = "This is a test case"
        user_typed = ""
        time_in_seconds = 60
        result = helpers.calculate_wpm(
            prompt, user_typed, time_in_seconds)
        self.assertEqual(result, (0, 0, 0))


class Test_sort_scores(unittest.TestCase):
    # Test order function
    def test_clean_input(self):
        scores = ["Matt 2: 0wpm, Easy mode, 4.3% accuracy, 0% consistency",
                  "Matt 3: 72wpm, Easy mode, 100.0% accuracy, 0% consistency",
                  "Matt 1: 65wpm, Easy mode, 100.0% accuracy, 78.18% consistency"]
        result = helpers.sort_scores(scores)
        self.assertEqual(result, ['Matt 3: 72wpm, Easy mode, 100.0% accuracy, 0% consistency',
                         'Matt 1: 65wpm, Easy mode, 100.0% accuracy, 78.18% consistency', 'Matt 2: 0wpm, Easy mode, 4.3% accuracy, 0% consistency'])

    # Duplicate scores don't need to be sorted, they remain in the order they were submitted
    def test_duplicate_input(self):
        scores = ["Matt 1: 72wpm, Easy mode, 100.0% accuracy, 0% consistency",
                  "Matt 2: 72wpm, Easy mode, 100.0% accuracy, 0% consistency",
                  "Matt 3: 72wpm, Easy mode, 100.0% accuracy, 0% consistency"]
        result = helpers.sort_scores(scores)
        self.assertEqual(result, ["Matt 1: 72wpm, Easy mode, 100.0% accuracy, 0% consistency",
                                  "Matt 2: 72wpm, Easy mode, 100.0% accuracy, 0% consistency",
                                  "Matt 3: 72wpm, Easy mode, 100.0% accuracy, 0% consistency"])

    # If no scores provided, return an empty list and don't crash
    def test_no_input(self):
        scores = []
        result = helpers.sort_scores(scores)
        self.assertEqual(result, [])


class Test_load_api(unittest.TestCase):
    # Tests API call to random words returns 50 words
    def test_random_words_count(self):
        result = helpers.load_api(
            "https://www.mit.edu/~ecprice/wordlist.10000")
        self.assertEqual(len(result.split()), 50)

    # Tests API call to random words returns a str
    def test_random_words_type(self):
        result = helpers.load_api(
            "https://www.mit.edu/~ecprice/wordlist.10000")
        self.assertEqual(type(result), type("result"))

    # Test API call to quote returns a str
    def test_quote_response(self):
        result = helpers.load_api("https://type.fit/api/quotes")
        self.assertEqual(type(result), type("result"))


class Test_username_unused(unittest.TestCase):
    @ patch("builtins.open", new_callable=mock_open, read_data="Matt: 77wpm, Easy mode, 100.0% accuracy, 84.52% consistency")
    def test_used(self, mock_file):
        username = 'Matt'
        self.assertEqual(helpers.username_unused(username), False)

    @ patch("builtins.open", new_callable=mock_open, read_data="Dave: 77wpm, Easy mode, 100.0% accuracy, 84.52% consistency")
    def test_unused(self, mock_file):
        username = 'Fred'
        self.assertEqual(helpers.username_unused(username), True)

    @ patch("builtins.open", new_callable=mock_open, read_data="Dave: 77wpm, Easy mode, 100.0% accuracy, 84.52% consistency")
    def test_empty(self, mock_file):
        username = ''
        self.assertEqual(helpers.username_unused(username), False)


class Test_key_logging(unittest.TestCase):
    def test_ascii(self):
        for key in range(32, 126):
            assert helpers.check_ascii_input(key) == True

    def test_esc(self):
        assert helpers.check_esc(27) == True

    def test_check_enter_input(self):
        assert helpers.check_enter_input(
            10) == True or helpers.check_enter_input(13) == True

    def test_check_backspace(self):
        assert helpers.check_backspace(
            127) == True or helpers.check_backspace(1) == False


if __name__ == "__main__":
    unittest.main()
