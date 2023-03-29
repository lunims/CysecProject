def valid_email(email):
    assert len(email) < 20
    assert len(email) > 9
    assert email.endswith(".com") or email.endswith(".de")
    assert '@' in email