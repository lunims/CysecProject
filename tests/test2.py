def test(s):
    if s[0] == 'a':
        if s[1] == 'b':
            if s[2] == 'c':
                if s[3] == 'd':
                    assert len(s) == 4
                else:
                    assert s[3] == 'i'
            else:
                assert len(s) == 3
                assert s[2] != 'd'
    else:
        if s[0] == 'z':
            assert len(s) == 1
        else:
            assert s.startswith("boing")
            assert len(s) == 6