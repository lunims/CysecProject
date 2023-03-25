def test(s):
    if s[0] == 'a':
        assert len(s) == 1
    else:
        assert len(s) != 3
        assert s[0] != 'z'
        assert s[1] == 'b'
        assert s[4] != 'm'
        assert s[7] != 't'