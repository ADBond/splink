import sqlglot


def test_sqlglot_version():
    major, minor, patch = sqlglot.__version__.split(".")
    absolute_version = 10_000 * int(major) + 100 * int(minor) + int(patch)
    assert absolute_version <= 27_26_00
