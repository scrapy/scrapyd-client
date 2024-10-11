import re


def assert_lines(actual, expected):
    if isinstance(expected, str):
        assert actual.splitlines() == expected.splitlines()
    else:
        lines = actual.splitlines()
        assert len(lines) == len(expected)
        for i, line in enumerate(lines):
            assert re.search(f"^{expected[i]}$", line), f"{line} does not match {expected[i]}"
