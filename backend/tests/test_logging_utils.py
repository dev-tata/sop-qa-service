
from app.logging_utils import get_logger

def test_get_logger_is_singleton_handlers():
    a = get_logger("x")
    b = get_logger("x")
    assert a is b
    assert len(a.handlers) >= 1
