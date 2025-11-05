import os
from fastapi import HTTPException, status

def get_api_key() -> str | None:
    """
    Runtime olarak çevresel değişkenden API_KEY okur.
    Testlerde veya CI'da pytest/conftest.py ile ayarlanmış olmalıdır.
    """
    return os.getenv("API_KEY")

def require_api_key(x_api_key: str):
    """
    İstek başına çağrılacak doğrulama fonksiyonu.
    - Eğer sunucuda API_KEY yapılandırılmamışsa 500 döner.
    - Eğer gelen header eşleşmiyorsa 401 döner.
    """
    API_KEY = get_api_key()
    if API_KEY is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured on server",
        )
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
