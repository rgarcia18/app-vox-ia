from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: str
    username: str
    display_name: str
    created_at: str
    last_login_at: Optional[str] = None
