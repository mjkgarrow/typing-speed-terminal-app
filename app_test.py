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


def test_measure_consistency():
    consistency = app.measure_consistency([65, 65, 65])
    assert consistency == 66.67
