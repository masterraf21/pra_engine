import unittest
import json
from pydantic import parse_obj_as
from src.critical_path.models import CriticalPath
from src.critical_path.process import compare_critical_path, compare_critical_path_v2
from src.utils.testing import get_json, write_json


def get_path_json(filename: str) -> list[CriticalPath]:
    data = get_json(filename)
    parsed_data = parse_obj_as(list[CriticalPath], data)
    return parsed_data


class TestCriticalPath(unittest.TestCase):
    def test_compare(self):
        baseline_paths = get_path_json('/data/paths_baseline.json')
        regress_paths = get_path_json('/data/paths_regress.json')

        result = compare_critical_path(baseline_paths, regress_paths)
        result_json = [r.dict() for r in result]
        write_json(json.dumps(result_json), '/testing/cpath_compare.json')

    def test_compare_v2(self):
        baseline_paths = get_path_json('/data/paths_baseline.json')
        regress_paths = get_path_json('/data/paths_regress.json')

        result = compare_critical_path_v2(baseline_paths, regress_paths)
        result_json = [r.dict() for r in result]
        write_json(json.dumps(result_json), '/testing/cpath_compare_v2.json')
