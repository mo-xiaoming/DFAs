from lib.regex import match


def test_empty_pattern():
    assert match("", "")


def test_literal():
    assert match("a", "a")
    assert match("aa", "aa")
    assert match("abc", "abc")
    assert not match("a", "b")
    assert not match("aa", "ab")


def test_star():
    assert match("b*", "")
    assert match("b*", "b")
    assert match("b*", "bb")
    assert match("b*", "bbb")
    assert match("ab*", "abbb")
    assert match("ab*", "a")
    assert match("ab*", "ab")
    assert not match("a*", "b")
    assert not match("a*", "bb")
    assert not match("a*", "ab")
    assert not match("a*", "ba")
    assert not match("a*", "aab")
