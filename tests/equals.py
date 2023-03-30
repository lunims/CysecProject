def eq(s):
    if s.startswith("te"):
        assert s == "testEquals"
    else:
        assert len(s) > 10