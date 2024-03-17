from enum import Enum


class UserRole(str, Enum):
    TEMPORAL = "temporal"
    USER = "user"
    ADMIN = "admin"


class Category(str, Enum):
    DOTNET = "dotnet"
    ADOBE = "adobe"
    JAVA = "java"