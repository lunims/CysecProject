def test(s):
    if len(s) < 20:
        assert s.startswith('abcdefg')
        assert s.endswith('defghij')