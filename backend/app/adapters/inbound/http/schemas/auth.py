from pydantic import BaseModel, field_validator
import re

class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username debe tener entre 3 y 50 caracteres")
        if not re.match(r'^[a-zA-Z0-9._@-]+$', v):
            raise ValueError("Username contiene caracteres inválidos")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6 or len(v) > 100:
            raise ValueError("Password debe tener entre 6 y 100 caracteres")
        return v
