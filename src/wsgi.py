import os  # pragma: no cover

from apps.base import create_app  # pragma: no cover

app = create_app(os.environ.get("STAGE"))  # pragma: no cover
