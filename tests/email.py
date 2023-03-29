def valid_email(email):
    assert email.endswith(".com")
    assert '@' in email