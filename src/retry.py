"""
Generic retry logic with exponential backoff and validation.

This module provides reusable retry functionality for API calls with:
- Exponential backoff for retryable errors
- Validation and correction loops
- Specific error handling for retryable vs non-retryable errors
"""

import time
from typing import Callable, Optional, Tuple, TypeVar

from openai import APIConnectionError, APIError, AuthenticationError, RateLimitError
from pydantic import ValidationError

from utils import configure_logger

logger = configure_logger()

T = TypeVar("T")

# Error categories
RETRYABLE_ERRORS = (RateLimitError, APIConnectionError, TimeoutError, ValidationError)
NON_RETRYABLE_ERRORS = (AuthenticationError, ValueError, KeyError)


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay


def call_with_retry(
    api_call: Callable[[], T],
    validator: Callable[[T], Tuple[bool, Optional[str]]],
    correction_builder: Optional[Callable[[str, str], Callable[[], T]]] = None,
    config: RetryConfig = None,
    case_id: str = "unknown",
) -> T:
    """
    Execute API call with retry logic, validation, and correction.

    Args:
        api_call: Function that makes the initial API call
        validator: Function that validates response, returns (is_valid, error_msg)
        correction_builder: Optional function that builds correction API call from (response_id, error_msg)
        config: Retry configuration (default: RetryConfig())
        case_id: Case ID for logging

    Returns:
        Validated response from API

    Raises:
        RuntimeError: If max retries exceeded without valid response
        Non-retryable errors: AuthenticationError, ValueError, etc.

    Example:
        >>> def make_call():
        >>>     return client.call(prompt)
        >>> def validate(response):
        >>>     if response.valid:
        >>>         return True, None
        >>>     return False, "Invalid response"
        >>> result = call_with_retry(make_call, validate, case_id="case123")
    """
    if config is None:
        config = RetryConfig()

    retries = 0
    last_response = None
    last_response_id = None

    while retries < config.max_retries:
        try:
            # Make API call (initial or correction)
            if retries == 0:
                logger.debug(f"[case {case_id}] Making initial API call")
                response = api_call()
            elif correction_builder and last_response_id:
                logger.debug(
                    f"[case {case_id}] Retry {retries}/{config.max_retries}: Making correction call"
                )
                # Build correction call with previous response_id and error message
                correction_call = correction_builder(last_response_id, last_error_msg)
                response = correction_call()
            else:
                # No correction builder, retry with same call
                logger.debug(
                    f"[case {case_id}] Retry {retries}/{config.max_retries}: Retrying same call"
                )
                response = api_call()

            last_response = response

            # Extract response_id if available for conversational correction
            if hasattr(response, "id"):
                last_response_id = response.id

            # Validate response
            is_valid, error_msg = validator(response)

            if is_valid:
                logger.debug(
                    f"[case {case_id}] Successfully validated response on attempt {retries + 1}"
                )
                return response

            # Invalid response, prepare for retry
            last_error_msg = error_msg
            logger.info(
                f"[case {case_id}] Validation failed on attempt {retries + 1}: {error_msg}"
            )
            retries += 1

        except RETRYABLE_ERRORS as e:
            # Network/rate limit errors - retry with exponential backoff
            wait_time = min(config.base_delay * (2**retries), config.max_delay)
            logger.warning(
                f"[case {case_id}] Retry {retries + 1}/{config.max_retries}: "
                f"Retryable error ({type(e).__name__}), waiting {wait_time:.1f}s: {e}"
            )
            time.sleep(wait_time)
            retries += 1

        except NON_RETRYABLE_ERRORS as e:
            # Authentication, value errors - fail immediately
            logger.error(
                f"[case {case_id}] Non-retryable error ({type(e).__name__}): {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            # Unexpected errors - log with stack trace and fail
            logger.error(
                f"[case {case_id}] Unexpected error ({type(e).__name__}): {e}",
                exc_info=True,
            )
            raise

    # Max retries exceeded
    error_msg = (
        f"Max retries ({config.max_retries}) exceeded for case {case_id}. "
        f"Last validation error: {last_error_msg if 'last_error_msg' in locals() else 'Unknown'}"
    )
    logger.error(error_msg)
    raise RuntimeError(error_msg)
