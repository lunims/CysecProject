def test(s):
    if len(s) == 1:
        assert s[0] != 'a'
        assert s[0] != 'b'
        assert s[0] != 'c'
        assert s[0] != 'd'
        assert s[0] != 'e'
        assert s[0] != 'f'
        assert s[0] != 'g'
        assert s[0] != 'h'
        assert s[0] != 'i'
        assert s[0] != 'j'
        assert s[0] != 'k'
        assert s[0] != 'l'
        assert s[0] != 'm'
        assert s[0] != 'n'
        assert s[0] != 'o'
    else:
        assert s[0] != 'A'
        assert s[1] == 'A'
        assert s[2] != 'A'
        assert s[3] == '('