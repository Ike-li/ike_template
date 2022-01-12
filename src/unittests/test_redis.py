import time
import uuid

import pytest

from extensions.redis_cluster import DuplicateRequest, assert_new_request


def test_duplicate_request():
    request_id = uuid.uuid4()
    assert_new_request("my-request", request_id, life_time_second=1)

    with pytest.raises(DuplicateRequest):
        assert_new_request("my-request", request_id, life_time_second=1)

    # 当时间过了，还是可以继续用相同的 request id 请求
    time.sleep(1.01)
    assert_new_request("my-request", request_id, life_time_second=1)
