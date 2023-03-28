def valid_email(email):
    assert len(email) < 20
    assert email.endswith("@gmx.de")