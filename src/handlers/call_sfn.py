from logger.decorator import lambda_auto_logging
from logger.my_logger import MyLogger
from uuid import uuid4
import boto3
from botocore.client import BaseClient
from utils import get_environ_values

logger = MyLogger(__name__)
environ_names = ['STATE_MACHINE_ARN']


@lambda_auto_logging(*environ_names)
def handler(event, context):
    main()


def main(sfn_client: BaseClient = boto3.client('stepfunctions')):
    state_machine_arn, = get_environ_values(environ_names)
    logger.info(state_machine_arn)
