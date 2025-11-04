
import os
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import Optional

API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key: Optional[str] = Security(api_key_header)):
    expected = os.environ.get("SHELVIA_API_KEY")
    if expected is None:
        raise HTTPException(status_code=500, detail="API key not configured on server")
    if not api_key or api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return api_key
