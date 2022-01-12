import pytest

from base_engine.controller.base_controller import BaseController


def test_base_controller():
    """
    基类
    """
    base_controller = BaseController(config={})
    assert base_controller


def test_base_controller_action():
    base_controller = BaseController(config={})
    with pytest.raises(NotImplementedError):
        base_controller.action()


def test_base_controller_update_config():
    base_controller = BaseController(config={})
    with pytest.raises(NotImplementedError):
        base_controller.update_config()
