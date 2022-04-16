import unittest
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
