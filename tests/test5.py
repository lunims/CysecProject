def test5(s):
    assert s.startswith("test")
    assert len(s) < 20
    assert s[5] == 'X'
    return True