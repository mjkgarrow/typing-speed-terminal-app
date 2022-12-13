import app
import unittest.mock
from unittest.mock import patch, mock_open
from unittest import mock
import unittest
import curses


# def test_main(window):
#     pass


# Test save_score_to_file is reading and writing to file correctly
@patch("builtins.open", new_callable=mock_open, read_data="Matt 1: 77wpm, 100.0% accuracy, 84.52% consistency, Easy mode")
def test_save_score_to_file(mock_file):
    assert app.save_score_to_file('Matt 3', 90, 100.0, 'Easy mode', 84.52) == [
        'Matt 3: 90wpm, 100.0% accuracy, 84.52% consistency, Easy mode',
        'Matt 1: 77wpm, 100.0% accuracy, 84.52% consistency, Easy mode']


# Test load_high_score is correctly reading a file
@patch("builtins.open", new_callable=mock_open, read_data="Matt 1: 77wpm, 100.0% accuracy, 84.52% consistency, Easy mode")
def test_load_file_read_file(mock_file):
    with mock.patch('os.listdir') as mocked_listdir:
        mocked_listdir.return_value = [mock_file]
        assert app.load_high_score() == [
            "Matt 1: 77wpm, 100.0% accuracy, 84.52% consistency, Easy mode"]


# Test load_high_score is correctly responding to an empty file
@patch("builtins.open", new_callable=mock_open, read_data="")
def test_load_file_empty_file(mock_file):
    with mock.patch('os.listdir') as mocked_listdir:
        mocked_listdir.return_value = [mock_file]
        assert app.load_high_score() == ["No high scores."]


# Test consistency function with no deviation
def test_measure_consistency():
    consistency = app.measure_consistency([65, 65, 65])
    assert consistency == 100


# Test consistency function with 0s
def test_measure_consistency_zero():
    consistency = app.measure_consistency([0, 0, 0])
    assert consistency == 0


# Test consistency function with only 1 input
def test_measure_consistency_1input():
    consistency = app.measure_consistency([100])
    assert consistency == 100.0


# Test wpm calculation with correct user input
def test_calculate_wpm():
    prompt = "This is a test case"
    user_typed = "This is a test case"
    time_in_seconds = 60
    assert app.calculate_wpm(
        prompt, user_typed, time_in_seconds) == (3, 3, 100.0)


# Test wpm calculation with correct some incorrect input
def test_calculate_wpm_incorrect():
    prompt = "This is a test case"
    user_typed = "This is a blur case"
    time_in_seconds = 60
    assert app.calculate_wpm(
        prompt, user_typed, time_in_seconds) == (3, 0, 78.9)


# Test wpm calculation with correct some no input
def test_calculate_wpm_no_input():
    prompt = "This is a test case"
    user_typed = ""
    time_in_seconds = 60
    assert app.calculate_wpm(
        prompt, user_typed, time_in_seconds) == (0, 0, 0)
