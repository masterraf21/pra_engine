import unittest
import json
from src.storage.redis import init_redis_client
import src.storage.retrieve as rret
import src.storage.store as rstore
import logging
import redis
import time
import json


class TestJson(unittest.TestCase):
    def test_list_float_json(self):
        a = [1.2, 1.3, 1.4, 1.5, 1.6]
        a_str = json.dumps(a)
        print(a_str)
        loaded = json.loads(a_str)
        loaded: list[float] = list(loaded)
        print(type(loaded))
        print(loaded)


class TestRedis(unittest.TestCase):
    # @classmethod
    # def setUpClass(cls) -> None:
    #     print("Setting Up Redis...")
    #     cls.connection = init_redis_client()
    #     return super().setUpClass()

    # @classmethod
    # def tearDownClass(cls) -> None:
    #     print("Closing Redis...")
    #     cls.connection.close()
    #     return super().tearDownClass()

    def test_init(self):
        conn = init_redis_client()
        check = conn.ping()
        self.assertTrue(check)

    def test_store(self):
        data = {"a": 1, "b": 2}
        data_json = json.dumps(data)
        key = str(time.time())
        rstore.store_json("test1", data_json)
        # check =
