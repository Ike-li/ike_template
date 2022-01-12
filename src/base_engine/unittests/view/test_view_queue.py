from base_engine.view.view_queue import ViewQueue


def test_view_queue():
    view_queue = ViewQueue()
    assert view_queue.queue == []


def test_view_queue_add():
    view_queue = ViewQueue()


def test_view_queue_all():
    view_queue = ViewQueue()
    assert view_queue.all() == []
