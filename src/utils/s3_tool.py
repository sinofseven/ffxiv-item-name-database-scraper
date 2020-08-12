eorzea_database = "eorzea_database"
xivapi = "xivapi"


def create_key_of_eorzea_database_item(process_id: str, page: int) -> str:
    return f"{process_id}/{eorzea_database}/{page:07}.json"


def create_key_of_xivapi_item(process_id: str, page: int) -> str:
    return f"{process_id}/{xivapi}/{page:07}.json"


def create_key_of_eorzea_database_merged_item(process_id: str) -> str:
    return f"{process_id}/merged_{eorzea_database}.json"


def create_key_of_xivapi_merged_item(process_id: str) -> str:
    return f"{process_id}/merged_{xivapi}.json"


def create_key_of_match_data(process_id: str) -> str:
    return f"{process_id}/result_match_data.json"


def create_key_of_irregular_data(process_id: str) -> str:
    return f"{process_id}/result_irregular_data.json"


def create_prefix_of_eorzea_database_item(process_id: str) -> str:
    return f"{process_id}/{eorzea_database}/"


def create_prefix_of_xivapi_item(process_id: str) -> str:
    return f"{process_id}/{xivapi}/"
