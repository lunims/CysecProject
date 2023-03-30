def all_features(s):
    if "so" in s:
        assert len(s) > 3
        assert len(s) < 12
        if s.startswith("x"):
            assert s.endswith("ye")
        else:
            assert s.endswith("ze")