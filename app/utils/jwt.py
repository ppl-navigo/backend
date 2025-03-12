from typing import Any, Union, Dict


def create_access_token(subject: Union[str, Any]) -> str:
    ...

def create_refresh_token(subject: Union[str, Any]) -> tuple:
    ...

def verify_password(plain_password: str, hashed_password: str) -> bool:
    ...

def get_password_hash(password: str) -> str:
    ...

def decode_token(token: str) -> Dict:
    ...

def revoke_refresh_token(user_id: str) -> bool:
    ...

def is_valid_refresh_token(user_id: str, token: str) -> bool:
    ...