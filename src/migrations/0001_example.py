from typing import Type

from cassandra.cqlengine.models import Model


def migrate():
    """迁移脚本示范"""
    MyModel: Type[Model] = None
    # FIXME 注意这个默认只取 1w 条数据
    if 10000 < MyModel.objects.count():
        raise Exception("数据量超过 1w，无法 migrate")

    objects = MyModel.objects.all()
    for _object in objects:
        _object.new_property = "init value"
        _object.save()
