from typing import List, Optional, Generator
import os


def get_environ_values(environ_names: List[str]) -> List[Optional[str]]:
    def process() -> Generator:
        for name in environ_names:
            yield os.getenv(name)

    return list(process())
