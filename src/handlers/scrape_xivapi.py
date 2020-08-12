import json
from typing import Tuple
from urllib.parse import quote
from urllib.request import Request, urlopen

import boto3
from botocore.client import BaseClient

from logger.decorator import lambda_auto_logging
from utils.lambda_tool import get_environ_values
from utils.s3_tool import create_key_of_xivapi_item

environ_names = ["TMP_DATA_BUCKET_NAME"]


@lambda_auto_logging(*environ_names)
def handler(event, context) -> dict:
    return main(event)


def main(event: dict, s3_client: BaseClient = boto3.client("s3")) -> dict:
    (tmp_data_bucket_name,) = get_environ_values(environ_names)
    process_id, page = parse_event(event)
    data = get_xivapi_data(page)
    put_data(process_id, page, data, tmp_data_bucket_name, s3_client)
    next_page = create_next_page(page, data)
    return create_result(process_id, next_page)


def parse_event(event: dict) -> Tuple[str, int]:
    return event["id"], int(event.get("xivapi_page", 1))


def get_xivapi_data(page: int) -> dict:
    base_url = "https://xivapi.com/item"
    option = {
        "limit": 3000,
        "columns": ",".join(
            [
                "ID",
                "Icon",
                "Name_de",
                "Name_en",
                "Name_fr",
                "Name_ja",
                "ItemSearchCategory.ID",
                "ItemSearchCategory.Name",
            ]
        ),
        "page": page,
    }
    query = "&".join([f"{k}={quote(str(v))}" for k, v in option.items()])
    url = f"{base_url}?{query}"
    headers = {"User-Agent": "python xivapi-scraper"}
    req = Request(url=url, headers=headers)
    resp = urlopen(req)
    return json.load(resp)


def put_data(
    process_id: str, page: int, data: dict, bucket_name: str, s3_client: BaseClient
):
    option = {
        "Bucket": bucket_name,
        "Key": create_key_of_xivapi_item(process_id, page),
        "Body": json.dumps(data["Results"], ensure_ascii=False).encode(),
        "ContentType": "application/json",
    }
    s3_client.put_object(**option)


def create_next_page(page: int, data: dict) -> int:
    return 0 if data["Pagination"]["PageTotal"] == page else (page + 1)


def create_result(process_id: str, next_page: int) -> dict:
    return {"id": process_id, "xivapi_page": next_page}
