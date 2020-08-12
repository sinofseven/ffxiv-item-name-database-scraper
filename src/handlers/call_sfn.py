import json
from datetime import datetime, timezone
from uuid import uuid4

import boto3
from botocore.client import BaseClient

from logger.decorator import lambda_auto_logging
from logger.my_logger import MyLogger
from utils.lambda_tool import get_environ_values

logger = MyLogger(__name__)
environ_names = ["STATE_MACHINE_ARN"]


@lambda_auto_logging(*environ_names)
def handler(event, context):
    main()


def main(sfn_client: BaseClient = boto3.client("stepfunctions")):
    (state_machine_arn,) = get_environ_values(environ_names)

    exec_id = f"{create_reversed_timestamp_id()}-{uuid4()}"
    option = {
        "stateMachineArn": state_machine_arn,
        "name": exec_id,
        "input": json.dumps({"id": exec_id}),
    }
    resp = sfn_client.start_execution(**option)
    logger.info("result start_execution", result=resp)


def create_reversed_timestamp_id() -> str:
    max_number = 9007199254740991
    length = len(str(max_number))
    rtid_num = max_number - int(datetime.now(timezone.utc).timestamp() * 1000)
    return f'{"0" * length}{rtid_num}'[-length:]
