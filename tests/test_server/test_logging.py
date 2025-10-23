"""Tests for logging configuration."""

import logging

# pylint: disable=unused-argument
import re
from typing import Final

import pytest

_LOGGING_FORMAT_RE: Final = re.compile(
    r"timestamp='.+' level='error' event='Test message' logger='django'",
)


@pytest.fixture(name='logger')
def logger_fixture() -> logging.Logger:
    """Returns the current logger instance."""
    return logging.getLogger('django')


@pytest.fixture(autouse=True)
def _redact_caplog_handlers(
    caplog: pytest.LogCaptureFixture,
    logger: logging.Logger,
) -> None:
    """Pytest inserts custom formatter, we need to reset it back."""
    # Force the structlog formatter on the caplog handler
    import structlog
    from structlog.processors import KeyValueRenderer, TimeStamper
    from structlog.stdlib import ProcessorFormatter

    formatter = ProcessorFormatter(
        processor=KeyValueRenderer(
            key_order=['timestamp', 'level', 'event', 'logger']
        ),
        foreign_pre_chain=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            TimeStamper(fmt='iso'),
        ],
    )
    caplog.handler.setFormatter(formatter)


def test_logging_format(
    caplog: pytest.LogCaptureFixture,
    logger: logging.Logger,
) -> None:
    """Ensures logging is done correctly."""
    message = 'Test message'

    logger.error(message)

    assert _LOGGING_FORMAT_RE.match(caplog.text)
