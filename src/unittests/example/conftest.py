import uuid

import pytest


@pytest.fixture
def user_id():
    return uuid.uuid4()
