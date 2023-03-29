def valid_email(email):
    assert email.endswith(".com") or email.endswith(".de")
    assert '@' in email