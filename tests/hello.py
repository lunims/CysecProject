def check_hello_world(string):
    if string.startswith("Hello"):
        assert string[6] == 'x'
    else:
        assert string[0] != 'z'