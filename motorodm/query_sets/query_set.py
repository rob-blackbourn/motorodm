from .instance_query_set import InstanceQuerySet
from .class_query_set import ClassQuerySet


class QuerySet:

    def __get__(self, instance, owner):
        if instance is None:
            return lambda db: ClassQuerySet(owner, db)
        else:
            return lambda db: InstanceQuerySet(instance, db)
