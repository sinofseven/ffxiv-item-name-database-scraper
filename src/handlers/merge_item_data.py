import json
from typing import List, Tuple

import boto3
from botocore.client import BaseClient

from logger.decorator import lambda_auto_logging
from logger.my_logger import MyLogger
from utils.lambda_tool import get_environ_values
from utils.s3_tool import (
    create_key_of_eorzea_database_merged_item,
    create_key_of_irregular_data,
    create_key_of_match_data,
    create_key_of_xivapi_merged_item,
)

environ_names = ["TMP_DATA_BUCKET_NAME"]
logger = MyLogger(__name__)


@lambda_auto_logging(*environ_names)
def handler(event, context):
    main(event)


def main(event: dict, s3_client: BaseClient = boto3.client("s3")):
    (tmp_data_bucket_name,) = get_environ_values(environ_names)
    process_id = get_process_id_from_event(event)

    key_of_eorzea_database = create_key_of_eorzea_database_merged_item(process_id)
    key_of_xivapi = create_key_of_xivapi_merged_item(process_id)

    eorzea_database = get_s3_data(
        tmp_data_bucket_name, key_of_eorzea_database, s3_client
    )
    xivapi = get_s3_data(tmp_data_bucket_name, key_of_xivapi, s3_client)

    match, irregular = exec_matching(eorzea_database, xivapi)

    key_of_match = create_key_of_match_data(process_id)
    put_s3_data(tmp_data_bucket_name, key_of_match, match, s3_client)

    if len(irregular) > 0:
        key_of_irregular = create_key_of_irregular_data(process_id)
        put_s3_data(tmp_data_bucket_name, key_of_irregular, irregular, s3_client)
        logger.error("has irregular data", count=len(irregular))


def get_process_id_from_event(event: dict) -> str:
    return event["id"]


def get_s3_data(bucket_name: str, key: str, s3_client: BaseClient) -> List[dict]:
    option = {"Bucket": bucket_name, "Key": key}
    resp = s3_client.get_object(**option)
    return json.load(resp["Body"])


def exec_matching(
    eorzea_database: List[dict], xivapi: List[dict]
) -> Tuple[List[dict], List[dict]]:
    match = []
    irregular = []
    for item in eorzea_database:
        parsed = [x for x in xivapi if x["Name_en"] == item["name"]]
        if len(parsed) == 1:
            api_item = parsed[0]
            match.append({**api_item, **{"EorzeaDatabaseId": item["id"]}})
        else:
            irregular.append({"eorzea_database": item, "xivapi": parsed})
    return match, irregular


def put_s3_data(bucket_name: str, key: str, data: List[dict], s3_client: BaseClient):
    option = {
        "Bucket": bucket_name,
        "Key": key,
        "Body": json.dumps(data, ensure_ascii=False).encode(),
        "ContentType": "application/json",
    }
    s3_client.put_object(**option)
