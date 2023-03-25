def test(s):
    if len(s) < 20:
        assert s.startsWith('abcdefg')
        assert s.endsWith('defghij')