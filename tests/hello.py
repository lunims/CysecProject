def check_hello_world(string):
    if string.startswith("Hello"):
        if string.endswith("World"):
            assert len(string) == 11
    else:
        assert len(string) < 12
