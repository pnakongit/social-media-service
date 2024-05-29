import uuid
from pathlib import Path

from django.utils.text import slugify


def upload_image_file_path(instance, filename: str) -> Path:
    extension = Path(filename).suffix
    filename = Path(f"{slugify(instance.id)}-{uuid.uuid4()}{extension}")
    directory = Path("upload", instance.__class__.__name__.lower())
    return directory / filename
