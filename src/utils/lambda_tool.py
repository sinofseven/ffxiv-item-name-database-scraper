import os
from typing import Generator, List


def get_environ_values(environ_names: List[str]) -> List[str]:
    def process() -> Generator:
        for name in environ_names:
            yield os.getenv(name)

    return list(process())
