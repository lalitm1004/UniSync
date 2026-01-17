from __future__ import annotations

import dotenv
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ERPCredentials:
    netid: str
    password: str

    @classmethod
    def from_env(cls) -> ERPCredentials:
        dotenv.load_dotenv()

        netid = os.getenv("SNU_NETID")
        password = os.getenv("SNU_PASSWORD")

        if not netid or not password:
            raise ValueError(
                "Missing credentials. Ensure SNU_NETID and SNU_PASSWORD are properly configured"
            )

        return cls(netid, password)
