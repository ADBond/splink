from .decorator import mark_with_dialects_excluding


@mark_with_dialects_excluding()
def test_dummy(dialect, test_helpers):
    helper = test_helpers[dialect]
