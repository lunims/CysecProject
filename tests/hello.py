def check_hello_world(string):
    if string.startswith("Hello"):
        if string.endswith("World"):
            assert len(string) == 11
    else:   #TODO else case for startswith and endswith does not work
        assert len(string) < 12
