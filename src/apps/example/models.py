from datetime import datetime

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model


class Person(Model):
    __table_name__ = "person"

    first_name = columns.Text(primary_key=True)
    last_name = columns.Text()

    created_at = columns.DateTime(default=datetime.utcnow)
