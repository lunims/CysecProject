def valid_email2(email):
    assert email.endswith('@gmx.de') or email.endswith('@aol.com') or email.endswith('@gmail.com')
    assert len(email) < 20