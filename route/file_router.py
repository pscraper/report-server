import hashlib
import os
from starlette.responses import FileResponse
from typing import Annotated, Any
from fastapi import APIRouter, File, Form, Query, HTTPException, status
from pathlib import Path
from model.enums import Category


router = APIRouter()


@router.head(path = "/check")
async def check_file(
    category: Annotated[str, Query()],
    filename: Annotated[str, Query()],
    md5: Annotated[str, Query()],
    sha256: Annotated[str, Query()]
) -> None:
    file_path = find_file(category, filename)
    
    with open(file_path, "rb") as fp:
        binary = fp.read()
        c_md5 = hashlib.md5(binary).hexdigest() 
        c_sha256 = hashlib.sha256(binary).hexdigest()
    
    if c_md5 == md5 and c_sha256 == sha256:
        raise HTTPException(status_code = status.HTTP_208_ALREADY_REPORTED)


@router.post(path = "/result", status_code = status.HTTP_200_OK)
async def upload_result_file(
    filename: Annotated[str, Form()],
    category: Annotated[Category, Form()],
    file: Annotated[bytes, File()] 
) -> None:
    storage = find_storage(category)
    with open(storage / filename, "wb") as fp:
        fp.write(file)
        

@router.get(path = "/office", status_code = status.HTTP_200_OK)
async def trigger_office_download() -> None:
    setup = Path.cwd() / "storage" / "setup.exe"
    xml = Path.cwd() / "storage" / "Office365ProPlus_x64.xml"
    cmd = f"start /b {str(setup)} /download {str(xml)}"
    os.system(cmd)


@router.get(path = "/{category}")
async def get_file_list_by_category(
    category: Annotated[Category, Path()]
) -> dict[str, Any]:
    storage = find_storage(category)
    files = filter(lambda file: file.is_file(), storage.iterdir())
    result = []

    for file in files:
        with open(file, "r", encoding = "utf8") as f:
            res = f.read()       
            result.append({
                "fileName": file.name,
                "fileDesc": res
            })

    return {"result": result}


@router.get(path = "/download/{category}/{filename}")
async def download_file(
    category: Annotated[Category, Path()],
    filename: Annotated[str, Path()]
) -> FileResponse:
    file_path = find_file(category, filename)
    return FileResponse(path = file_path)

    
def find_storage(category: Category) -> Path:
    storage = Path.cwd() / "storage" / category.value

    if not storage.exists():
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"Can't Find Storage Path {str(storage)}"
        )
    
    return storage


def find_file(category: Category, filename: str) -> Path:
    storage = find_storage(category)
    file_path = storage / filename

    if file_path.exists() and file_path.is_file():
        return file_path
    
    raise HTTPException(
        status_code = status.HTTP_400_BAD_REQUEST,
        detail = f"Can't Find File {str(file_path)}"
    )
    