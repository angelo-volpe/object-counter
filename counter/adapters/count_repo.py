from typing import List

from pymongo import MongoClient
from sqlalchemy import create_engine, text

from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo


class CountInMemoryRepo(ObjectCountRepo):

    def __init__(self):
        self.store = dict()

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        if object_classes is None:
            return list(self.store.values())

        return [self.store.get(object_class) for object_class in object_classes]

    def update_values(self, new_values: List[ObjectCount]):
        for new_object_count in new_values:
            key = new_object_count.object_class
            try:
                stored_object_count = self.store[key]
                self.store[key] = ObjectCount(key, stored_object_count.count + new_object_count.count)
            except KeyError:
                self.store[key] = ObjectCount(key, new_object_count.count)


class CountMongoDBRepo(ObjectCountRepo):

    def __init__(self, host, port, database):
        self.__host = host
        self.__port = port
        self.__database = database

    def __get_counter_col(self):
        client = MongoClient(self.__host, self.__port)
        db = client[self.__database]
        counter_col = db.counter
        return counter_col

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        counter_col = self.__get_counter_col()
        query = {"object_class": {"$in": object_classes}} if object_classes else None
        counters = counter_col.find(query)
        object_counts = []
        for counter in counters:
            object_counts.append(ObjectCount(counter['object_class'], counter['count']))
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        counter_col = self.__get_counter_col()
        for value in new_values:
            counter_col.update_one({'object_class': value.object_class}, {'$inc': {'count': value.count}}, upsert=True)


class CountPostgreSQLRepo(ObjectCountRepo):

    def __init__(self, host, port, database, user, password):
        self.__engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

    def __build_query(self, object_classes: List[str]):
        query = "select object_class, count from counter"
        if object_classes:
            object_classes_str = "'" + "','".join(object_classes) + "'"
            query += f" where object_class in ({object_classes_str})"
        return query

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        query = self.__build_query(object_classes)
        with self.__engine.connect() as conn:
            counters = conn.execute(text(query))
        object_counts = []
        for counter in counters:
            object_counts.append(ObjectCount(counter[0], counter[1]))
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        for value in new_values:
            with self.__engine.connect() as conn:
                conn.execute(text(f"""INSERT INTO counter (object_class, count) 
                                      VALUES ('{value.object_class}', {value.count}) ON CONFLICT (object_class) 
                                      DO UPDATE SET count = counter.count+{value.count}"""))
                conn.commit()