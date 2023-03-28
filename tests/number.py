def number(s):
    assert len(s) == 5
    assert s.startswith('06')
    assert s[2] == '0' or s[2] == '1' or s[2] == '2' or s[2] == '3' or s[2] == '4' or s[2] == '5' or s[2] == '6' or s[
        2] == '7' or s[2] == '8' or s[2] == '9'
    assert s[3] == '0' or s[3] == '1' or s[3] == '2' or s[3] == '3' or s[3] == '4' or s[3] == '5' or s[3] == '6' or s[
        3] == '7' or s[3] == '8' or s[3] == '9'
    assert s[4] == '0' or s[4] == '1' or s[4] == '2' or s[4] == '3' or s[4] == '4' or s[4] == '5' or s[4] == '6' or s[
        4] == '7' or s[4] == '8' or s[4] == '9'