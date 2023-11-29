import pytest


# TO show full assert errors from helper file
# https://stackoverflow.com/questions/41522767/pytest-assert-introspection-in-helper-function
pytest.register_assert_rewrite('tests.helper')
