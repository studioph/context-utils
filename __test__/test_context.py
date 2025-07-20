import logging

import pytest

import context_utils


def func_that_throws(num: int) -> int:
    """Dummy function that throws an error on even numbers"""
    if num % 2 == 0:
        raise ValueError(num)
    return num


class MyError(Exception): ...


def test_log_errors(caplog):
    with context_utils.log_errors(logging.getLogger(), ValueError):
        func_that_throws(2)
    assert "ValueError" in caplog.text


def test_log_errors_loop():
    results = []

    for i in range(5):
        with context_utils.log_errors(logging.getLogger(), ValueError):
            results.append(func_that_throws(i))
    assert results == [1, 3]


def test_rethrow():
    with pytest.raises(MyError), context_utils.rethrow(ValueError, as_=MyError):
        func_that_throws(2)
