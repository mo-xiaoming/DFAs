from lib.regex import match


def test_empty_pattern():
    assert match("", "")


def test_literal():
    assert match("a", "a")
    assert not match("a", "b")


def test_dot():
    assert match(".", "a")
    assert not match(".", "")
