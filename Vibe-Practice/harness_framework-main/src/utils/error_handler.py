"""에러 분류 및 로깅."""

import logging
import sys
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "wave_academy.log", encoding="utf-8"),
    ],
)

_logger = logging.getLogger("wave_academy")

F = TypeVar("F", bound=Callable[..., Any])


class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


def log_error(
    severity: Severity,
    module: str,
    message: str,
    details: str | None = None,
    exc: BaseException | None = None,
) -> None:
    full_msg = f"[{module}] {message}"
    if details:
        full_msg += f" | {details}"

    if severity in (Severity.CRITICAL, Severity.HIGH):
        _logger.error(full_msg, exc_info=exc)
    elif severity == Severity.MEDIUM:
        _logger.warning(full_msg, exc_info=exc)
    else:
        _logger.info(full_msg)


def wrap(fn: Callable, module: str, severity: Severity = Severity.HIGH) -> Callable:
    """함수를 감싸 에러를 분류/로깅한다. CRITICAL/HIGH는 re-raise, MEDIUM은 None 반환."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            log_error(severity, module, str(exc), exc=exc)
            if severity in (Severity.CRITICAL, Severity.HIGH):
                raise
            return None

    return wrapper
