import os
import sys
from functools import wraps
from typing import Callable, List, Tuple

import boto3
import botocore

from .json_log_formatter import LAMBDA_REQUEST_ID_ENVIRONMENT_VALUE_NAME
from .my_logger import MyLogger

logger = MyLogger(__name__)


def get_environments(extra_environment_value_names: List[str]) -> dict:
    result = {x: os.getenv(x) for x in extra_environment_value_names}
    return result


def lambda_auto_logging(
    *extra_environment_value_names: str,
    throw_exception: bool = True,
    alert_unexpected_exception: bool = True,
) -> Callable:
    def wrapper(handler):
        @wraps(handler)
        def decorator(event, context):
            try:
                # LogにLambdaのRequestIdを出力するために環境変数として保存する
                os.environ[
                    LAMBDA_REQUEST_ID_ENVIRONMENT_VALUE_NAME
                ] = context.aws_request_id
            except Exception as e:
                logger.warning(f"Exception occurred: {e}")

            try:
                logger.info(
                    "event, python version, boto3 version, environment values",
                    event=event,
                    versions={
                        "python": sys.version,
                        "boto3": boto3.__version__,
                        "botocore": botocore.__version__,
                    },
                    environment_values=get_environments(
                        list(extra_environment_value_names)
                    ),
                )
            except Exception as e:
                logger.warning(f"Exception occurred: {e}")

            try:
                result = handler(event, context)
                logger.info("lambda result", result=result)
                return result
            except Exception as e:
                # Handler側でエラー処理することがあるので、アラート対象に
                if alert_unexpected_exception:
                    logger.error(f"Exception occurred: {e}")
                else:
                    logger.warning(f"Exception occurred: {e}")
                if throw_exception:
                    raise

        return decorator

    return wrapper
