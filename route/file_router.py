import hashlib
from typing import Annotated
from fastapi import APIRouter, File, Form, Query, HTTPException, status
from pathlib import Path


router = APIRouter()


@router.head(path = "/check")
def check_file(
    filename: Annotated[str, Query()],
    category: Annotated[str, Query()],
    md5: Annotated[str, Query()],
    sha256: Annotated[str, Query()]
) -> None:
    storage = Path.cwd() / "storage" / category
    filepath = storage / filename
    
    if filepath.exists():
        with open(filepath, "rb") as fp:
            binary = fp.read()
            c_md5 = hashlib.md5(binary).hexdigest() 
            c_sha256 = hashlib.sha256(binary).hexdigest()
        
        if not (c_md5 == md5 and c_sha256 == sha256):
            raise HTTPException(status_code = status.HTTP_208_ALREADY_REPORTED)


@router.post(path = "/result", status_code = status.HTTP_200_OK)
def upload_result_file(
    filename: Annotated[str, Form()],
    category: Annotated[str, Form()],
    file: Annotated[bytes, File()] 
) -> None:
    storage = Path.cwd() / "storage" / category
    
    if not storage.exists():
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"Can't Find Storage Path {str(storage)}"
        )
    
    with open(storage / filename, "wb") as fp:
        fp.write(file)