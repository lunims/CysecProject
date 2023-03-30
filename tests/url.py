def valid_url(url):
    assert url.startswith("https://") or url.startswith("http://")
    assert url.endswith(".com") or url.endswith(".de")