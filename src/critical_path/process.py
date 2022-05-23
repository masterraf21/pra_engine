
from pydash import sort_by
from src.config import get_settings

from .constants import LATENCY_THRESHOLD
from .models import ComparisonResult, CriticalPath, PathDuration, Result

env = get_settings()


def map_crticial_path(cps: list[CriticalPath]) -> dict[str, list[PathDuration]]:
    res: dict[str, list[PathDuration]] = {}
    for cp in cps:
        res[cp.root] = cp.durations
    return res


def fill_realtime_durations(root: str, durations: list[PathDuration]) -> list[ComparisonResult]:
    res: list[ComparisonResult] = []
    for duration in durations:
        res.append(ComparisonResult(
            root=root,
            baseline=duration.duration,
        ))
    return res


def fill_baseline_durations(root: str, durations: list[PathDuration]) -> list[ComparisonResult]:
    res: list[ComparisonResult] = []
    for duration in durations:
        res.append(ComparisonResult(
            root=root,
            realtime=duration.duration,
        ))
    return res


def check_suspected(diff: float, threshold: float) -> bool:
    return diff >= threshold+10 or diff >= threshold-10


def sort_result_diff(input: list[ComparisonResult]
                     | list[ComparisonResult]) -> list[ComparisonResult] | list[ComparisonResult]:
    return sort_by(input, 'diff', reverse=True)


def compare_critical_path(baseline: list[PathDuration],
                          realtime: list[PathDuration],
                          threshold: int = LATENCY_THRESHOLD) -> Result:
    suspected: list[ComparisonResult] = []
    normal: list[ComparisonResult] = []

    # map baseline data
    baseline_lookup: dict[str, float] = {}
    for duration in baseline:
        baseline_lookup[duration.operation] = duration.duration

    # compare realtime to map
    for path_duration in realtime:
        if path_duration.operation in baseline_lookup:
            operation = path_duration.operation
            baseline_duration = baseline_lookup[operation]
            realtime_duration = path_duration.duration
            diff = round(realtime_duration-baseline_duration, 3)
            suspected_check = check_suspected(diff, threshold)
            comparison = ComparisonResult(
                operation=operation,
                baseline=baseline_duration,
                realtime=realtime_duration,
                diff=diff,
                suspected=suspected_check
            )

            if suspected_check:
                suspected.append(comparison)
            else:
                normal.append(comparison)
    # sort and return
    suspected = sort_result_diff(suspected)
    normal = sort_result_diff(normal)

    return Result(suspected=suspected, normal=normal)
