def valid_url2(email):
    if email.startswith("http://") or email.startswith("https://"):
        assert len(email) > 10
        assert email.endswith(".de")
