import json
from typing import List, Tuple
from urllib.request import urlopen

import boto3
from botocore.client import BaseClient
from bs4 import BeautifulSoup

from logger.decorator import lambda_auto_logging
from utils.lambda_tool import get_environ_values
from utils.s3_tool import create_key_of_eorzea_database_item

environ_names = ["TMP_DATA_BUCKET_NAME"]


@lambda_auto_logging(*environ_names)
def handler(event: dict, context) -> dict:
    return main(event)


def main(event: dict, s3_client: BaseClient = boto3.client("s3")) -> dict:
    (tmp_data_bucket_name,) = get_environ_values(environ_names)
    process_id, page = parse_event(event)
    text = get_html_document(page)
    data = parse_data(text)
    put_data(process_id, page, data, tmp_data_bucket_name, s3_client)
    next_page = create_next_page(page, data)
    return create_result(process_id, next_page)


def parse_event(event: dict) -> Tuple[str, int]:
    return event["id"], int(event.get("database_page", 1))


def get_html_document(page: int) -> str:
    url = f"https://na.finalfantasyxiv.com/lodestone/playguide/db/item/?page={page}"
    return urlopen(url).read().decode()


def parse_item_id(url: str) -> str:
    index = -2 if url[-1] == "/" else -1
    return url.split("/")[index]


def parse_data(text: str) -> List[dict]:
    result = []
    bs = BeautifulSoup(text, "html.parser")
    trs = bs.select("table#character tbody tr")
    for tr in trs:
        img = tr.select_one("img")
        anchor = tr.select_one("a.db_popup.db-table__txt--detail_link")
        result.append(
            {
                "id": parse_item_id(anchor["href"]),
                "name": anchor.text,
                "icon": img["src"],
            }
        )

    return result


def put_data(
    process_id: str,
    page: int,
    data: List[dict],
    bucket_name: str,
    s3_client: BaseClient,
):
    option = {
        "Bucket": bucket_name,
        "Key": create_key_of_eorzea_database_item(process_id, page),
        "Body": json.dumps(data, ensure_ascii=False).encode(),
        "ContentType": "application/json",
    }
    s3_client.put_object(**option)


def create_next_page(page: int, data: List[dict]) -> int:
    return 0 if len(data) == 0 else (page + 1)


def create_result(process_id: str, next_page: int) -> dict:
    return {"id": process_id, "database_page": next_page}
