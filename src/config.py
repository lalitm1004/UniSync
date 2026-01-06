from __future__ import annotations

import dotenv
import os
from dataclasses import dataclass
from typing import Dict


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


@dataclass(frozen=True)
class GoogleOAuthConfig:
    client_id: str
    client_secret: str

    @classmethod
    def from_env(cls) -> GoogleOAuthConfig:
        dotenv.load_dotenv()

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "Missing cresentials. Ensure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are properly configured"
            )

        return cls(client_id=client_id, client_secret=client_secret)

    def to_client_config(self) -> Dict:
        return {
            "installed": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }
