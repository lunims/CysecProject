def test(s):
    if len(s) < 20:
        assert s.startswith('abcdefg')
        assert s[8] == 'z' or s[8] == 'a'
        assert s.endswith('defghij')