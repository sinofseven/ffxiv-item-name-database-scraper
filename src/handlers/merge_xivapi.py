import json
from typing import Iterator, List

import boto3
from botocore.client import BaseClient

from logger.decorator import lambda_auto_logging
from utils.lambda_tool import get_environ_values
from utils.s3_tool import create_key_of_xivapi_merged_item, create_prefix_of_xivapi_item

environ_names = ["TMP_DATA_BUCKET_NAME"]


@lambda_auto_logging(*environ_names)
def handler(event, context):
    main(event)
    return event


def main(event: dict, s3_client: BaseClient = boto3.client("s3")):
    (tmp_data_bucket_name,) = get_environ_values(environ_names)
    process_id = get_process_id_from_event(event)
    keys = list_keys(process_id, tmp_data_bucket_name, s3_client)
    data = merge(keys, tmp_data_bucket_name, s3_client)
    put_data(process_id, data, tmp_data_bucket_name, s3_client)


def get_process_id_from_event(event: dict) -> str:
    return event["id"]


def list_keys(
    process_id: str, bucket_name: str, s3_client: BaseClient, token=None
) -> List[str]:
    option = {"Bucket": bucket_name, "Prefix": create_prefix_of_xivapi_item(process_id)}
    if token is not None:
        option["ContinuationToken"] = token
    resp = s3_client.list_objects_v2(**option)
    result = [x["Key"] for x in resp.get("Contents", [])]
    if "NextContinuationToken" in resp:
        result += list_keys(
            process_id, bucket_name, s3_client, token=resp["NextContinuationToken"]
        )
    return result


def get_data(bucket: str, key: str, s3_client: BaseClient) -> List[dict]:
    option = {"Bucket": bucket, "Key": key}
    resp = s3_client.get_object(**option)
    return json.load(resp["Body"])


def merge(keys: List[str], bucket_name: str, s3_client: BaseClient) -> List[dict]:
    def executor() -> Iterator[dict]:
        for key in keys:
            data = get_data(bucket_name, key, s3_client)
            for item in data:
                yield item

    return list(executor())


def put_data(
    process_id: str, data: List[dict], bucket_name: str, s3_client: BaseClient
):
    option = {
        "Bucket": bucket_name,
        "Key": create_key_of_xivapi_merged_item(process_id),
        "Body": json.dumps(data, ensure_ascii=False).encode(),
        "ContentType": "application/json",
    }
    s3_client.put_object(**option)
