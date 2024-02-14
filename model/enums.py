from enum import Enum


class UserRole(str, Enum):
    TEMPORAL = "temporal"
    USER = "user"
    ADMIN = "admin"