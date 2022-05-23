import unittest
import json
from src.critical_path.process import compare_critical_path, compare_critical_path_v2
from src.critical_path.process import compare_critical_path
from src.utils.testing import write_json, get_path_json, get_path_v3


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

    def test_compare_v3(self):
        baseline_path = get_path_v3('/data/traces_baseline.json')
        realtime_path = get_path_v3('/data/traces_regress.json')

        result = compare_critical_path(
            baseline_path,
            realtime_path
        )
        # result_json = [r.dict() for r in result]
        write_json(json.dumps(result.dict()), '/testing/cpath_compare_v3.json')
