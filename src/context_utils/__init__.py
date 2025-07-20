import contextlib
import time
from collections.abc import Callable
from logging import Logger
from types import TracebackType
from typing import Self, Unpack


@contextlib.contextmanager
def rethrow(
    *errors: Unpack[Exception], as_: Exception = RuntimeError, **exception_kwargs
):
    """Catches one or more exceptions, and rethrows them as another exception.
    Intended to be used for aggregating more specific, internal exception types to expose a single, more unifed exception type

    Args:
        *errors: The exception(s) to catch.
        as_: The exception to re-throw the caught exception as
        **exception_kwargs: Additional kwargs to pass to the re-thrown exception

    Raises:
        Type[Exception]: The exception type provided to the `as_` argument, otherwise `RuntimeError`
    """
    try:
        yield
    except errors as error:
        raise as_(error, **exception_kwargs) from error


@contextlib.contextmanager
def log_errors(logger: Logger, *error_types: Unpack[Exception]):
    """Catches and logs non-fatal errors.
    Similar to `contextlib.suppress` except it adds a logging call at the `ERROR` level.

    Args:
        logger: The logger instance to use for logging the error.
        *error_types: The exception(s) to catch and messages for.
    """
    try:
        yield
    except error_types as error:
        logger.error("%r", error)


class timer(contextlib.AbstractContextManager):
    """Context manager for timing blocks of code.
    Can optionally print the resulting duration at the end.

    Attributes:
        start (float): The start timestamp
        end (float): The end timestamp
        duration (float): The difference between the start and end timestamps
    """

    def __init__(
        self, __print: bool = False, print_func: Callable[[str], None] = print
    ) -> None:
        """Initializes a new timer instance with the given settings.

        Args:
            __print: Whether or not to print the duration that was recorded.
            print_func: The function used to print the duration if `__print` is `True`. Defaults to `print`
        """
        self.start = self.end = self.duration = None
        self._print = __print
        self._print_func = print_func

    def __enter__(self) -> Self:
        self.start = time.time()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ):
        self.end = time.time()
        self.duration = self.end - self.start
        if self._print:
            self._print_func(f"Timer: {self.formatted}")

    @property
    def formatted(self) -> str:
        mins = self.duration // 60
        secs = self.duration % 60
        return f"{mins}m{round(secs, 2)}s"
