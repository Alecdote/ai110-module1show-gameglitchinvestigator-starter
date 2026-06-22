from logic_utils import check_guess
import os
import sys
from unittest.mock import MagicMock

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result[0] == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result[0] == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result[0] == "Too Low"



# --- Make app.py importable from the subfolder --------------------------------
APP_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ai110-module1show-gameglitchinvestigator-starter",
)
sys.path.insert(0, APP_DIR)

# --- Neutralize Streamlit so importing app.py doesn't launch/execute UI -------
# MagicMock returns a new mock for any attribute or call, so st.title(...),
# st.session_state, st.columns() -> (m, m, m), etc. all silently succeed.
mock_st = MagicMock()
mock_st.columns.return_value = (MagicMock(), MagicMock(), MagicMock())
# Widgets whose return values feed real logic must return real values, not
# MagicMocks: selectbox -> a difficulty string used as a dict key.
mock_st.sidebar.selectbox.return_value = "Normal"


# Streamlit's session_state supports BOTH attribute access (st.session_state.x)
# and membership tests ("x" not in st.session_state). A plain dict only does the
# latter, so we use a tiny shim that backs attributes with a dict.
class FakeSessionState:
    def __init__(self):
        object.__setattr__(self, "_d", {})

    def __getattr__(self, name):
        try:
            return self._d[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self._d[name] = value

    def __contains__(self, name):
        return name in self._d


mock_st.session_state = FakeSessionState()
sys.modules["streamlit"] = mock_st

import app  # noqa: E402  (import after the stub and path setup)


# -----------------------------------------------------------------------------
# get_range_for_difficulty
# -----------------------------------------------------------------------------
class TestGetRange:
    def test_easy(self):
        assert app.get_range_for_difficulty("Easy") == (1, 20)

    def test_normal(self):
        assert app.get_range_for_difficulty("Normal") == (1, 100)

    def test_hard(self):
        assert app.get_range_for_difficulty("Hard") == (1, 50)

    def test_low_never_exceeds_high(self):
        for diff in ["Easy", "Normal", "Hard"]:
            low, high = app.get_range_for_difficulty(diff)
            assert low <= high


# -----------------------------------------------------------------------------
# parse_guess
# -----------------------------------------------------------------------------
class TestParseGuess:
    def test_valid_integer(self):
        ok, value, err = app.parse_guess("42")
        assert ok is True and value == 42 and err is None

    def test_valid_float_is_truncated(self):
        ok, value, err = app.parse_guess("7.9")
        assert ok is True and value == 7 and err is None

    def test_negative_number(self):
        ok, value, err = app.parse_guess("-5")
        assert ok is True and value == -5

    def test_none_input(self):
        ok, value, err = app.parse_guess(None)
        assert ok is False and value is None and err == "Enter a guess."

    def test_empty_string(self):
        ok, value, err = app.parse_guess("")
        assert ok is False and value is None and err == "Enter a guess."

    def test_non_numeric(self):
        ok, value, err = app.parse_guess("abc")
        assert ok is False and value is None and err == "That is not a number."

    def test_whitespace_only(self):
        ok, value, err = app.parse_guess("   ")
        assert ok is False and err == "That is not a number."


# -----------------------------------------------------------------------------
# check_guess  (expects corrected hint directions)
# -----------------------------------------------------------------------------
class TestCheckGuess:
    def test_correct_guess_wins(self):
        outcome, message = app.check_guess(50, 50)
        assert outcome == "Win"
        assert "Correct" in message

    def test_too_high_tells_player_to_go_lower(self):
        outcome, message = app.check_guess(80, 50)
        assert outcome == "Too High"
        assert "LOWER" in message

    def test_too_low_tells_player_to_go_higher(self):
        outcome, message = app.check_guess(20, 50)
        assert outcome == "Too Low"
        assert "HIGHER" in message

    def test_boundary_just_above(self):
        outcome, _ = app.check_guess(51, 50)
        assert outcome == "Too High"

    def test_boundary_just_below(self):
        outcome, _ = app.check_guess(49, 50)
        assert outcome == "Too Low"

    def test_int_path_across_range(self):
        for guess in range(1, 11):
            outcome, _ = app.check_guess(guess, 5)
            if guess < 5:
                assert outcome == "Too Low"
            elif guess > 5:
                assert outcome == "Too High"
            else:
                assert outcome == "Win"


# -----------------------------------------------------------------------------
# update_score  (expects: first-try win = 100, symmetric -5 penalties)
# -----------------------------------------------------------------------------
class TestUpdateScore:
    def test_first_try_win_is_100(self):
        assert app.update_score(0, "Win", attempt_number=1) == 100

    def test_win_decreases_with_more_attempts(self):
        s1 = app.update_score(0, "Win", attempt_number=1)
        s2 = app.update_score(0, "Win", attempt_number=2)
        s3 = app.update_score(0, "Win", attempt_number=3)
        assert s1 > s2 > s3

    def test_win_bonus_has_a_floor_of_10(self):
        assert app.update_score(0, "Win", attempt_number=50) == 10

    def test_win_adds_to_existing_score(self):
        assert app.update_score(0, "Win", attempt_number=1) <= 100

    def test_too_high_loses_5(self):
        assert app.update_score(20, "Too High", attempt_number=3) == 15

    def test_too_low_loses_5(self):
        assert app.update_score(20, "Too Low", attempt_number=3) == 15

    def test_wrong_guesses_are_symmetric(self):
        for attempt in range(1, 9):
            high = app.update_score(50, "Too High", attempt_number=attempt)
            low = app.update_score(50, "Too Low", attempt_number=attempt)
            assert high == low

    def test_wrong_guess_never_increases_score(self):
        for attempt in range(1, 9):
            assert app.update_score(50, "Too High", attempt_number=attempt) <= 50
            assert app.update_score(50, "Too Low", attempt_number=attempt) <= 50



# -----------------------------------------------------------------------------
# Integration-style checks using only the logic functions
# -----------------------------------------------------------------------------
class TestGameFlow:
    def test_secret_within_range(self):
        import random
        for diff in ["Easy", "Normal", "Hard"]:
            low, high = app.get_range_for_difficulty(diff)
            for _ in range(100):
                secret = random.randint(low, high)
                assert low <= secret <= high

    def test_typical_two_guess_win(self):
        secret = 50
        score = 0
        outcome, msg = app.check_guess(30, secret)
        assert outcome == "Too Low" and "HIGHER" in msg
        score = app.update_score(score, outcome, attempt_number=1)
        assert score == -5
        outcome, msg = app.check_guess(50, secret)
        assert outcome == "Win"
        score = app.update_score(score, outcome, attempt_number=2)
        assert score == -5 + 90  # 85

    def test_invalid_then_valid_guess(self):
        ok, _, _ = app.parse_guess("oops")
        assert not ok
        ok, value, _ = app.parse_guess("10")
        assert ok and value == 10
