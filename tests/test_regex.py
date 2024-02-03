from lib.regex import match


def test_empty_pattern():
    assert match("", "")


def test_literal():
    assert match("a", "a")
    assert match("aa", "aa")
    assert match("abc", "abc")
    assert not match("a", "b")
    assert not match("aa", "ab")


def test_alternation():
    assert match("a|b", "a")
    assert match("a|b", "b")
    assert not match("a|b", "")
    assert not match("a|b", "c")
    assert match("a|b|c", "a")
    assert match("a|b|c", "b")
    assert match("a|b|c", "c")
    assert not match("a|b|c", "")
    assert not match("a|b|c", "d")
    assert match("a|b|c|d", "a")
    assert match("a|b|c|d", "b")
    assert match("a|b|c|d", "c")
    assert match("a|b|c|d", "d")
    assert not match("a|b|c|d", "")
    assert not match("a|b|c|d", "e")


def test_dot():
    assert match("a.b", "acb")
    assert match("a.b", "aab")
    assert match("a.b", "abb")
    assert not match("a.b", "")
    assert not match("a.b", "a")
    assert not match("a.b", "f")
    assert not match("a.b", "ab")
    assert not match("a.b", "bbb")
    assert not match("a.b", "abbb")


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
