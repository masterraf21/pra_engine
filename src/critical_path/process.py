from typing import Optional

from pydash import sort_by
from src.config import get_settings

from .constants import LATENCY_THRESHOLD
from .models import ComparisonResult, CriticalPath, PathDuration

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
    return diff >= threshold


def sort_result_diff(input: list[ComparisonResult]) -> list[ComparisonResult]:
    return sort_by(input, 'diff', True)


def compare_critical_path_v2(baseline: list[CriticalPath],
                             realtime: list[CriticalPath],
                             threshold: int = LATENCY_THRESHOLD) -> list[ComparisonResult]:
    res: list[ComparisonResult] = []

    baseline_map = map_crticial_path(baseline)
    realtime_map = map_crticial_path(realtime)

    if env.test:
        print(f"num of realtime root: {len(realtime_map)}")

    for i, realtime_root in enumerate(realtime_map.keys()):
        if env.test:
            print(f"root {i}: {realtime_root}\n")
        lookup: dict[str, float] = {}
        realtime_path_durations = realtime_map[realtime_root]
        baseline_path_durations: list[PathDuration] | None = None

        if realtime_root in baseline_map.keys():
            baseline_path_durations = baseline_map[realtime_root]
        else:
            continue

        for duration in baseline_path_durations:
            lookup[duration.operation] = duration.duration

        for path_duration in realtime_path_durations:
            if path_duration.operation in lookup:
                baseline_duration = lookup[path_duration.operation]
                realtime_duration = path_duration.duration
                diff = realtime_duration-baseline_duration
                suspected = check_suspected(diff, threshold)
                if suspected:
                    comparison = ComparisonResult(
                        root=realtime_root,
                        operation=path_duration.operation,
                        baseline=baseline_duration,
                        realtime=realtime_duration,
                        diff=diff,
                        suspected=check_suspected(diff, threshold)
                    )
                    res.append(comparison)

    return sort_result_diff(res)


def compare_critical_path(baseline: list[CriticalPath],
                          realtime: list[CriticalPath]) -> list[ComparisonResult]:
    res: list[ComparisonResult] = []

    baseline_map = map_crticial_path(baseline)
    realtime_map = map_crticial_path(realtime)

    for baseline_root in baseline_map.keys():
        lookup: dict[str, float] = {}
        realtime_durations: Optional[list[PathDuration]] = None
        baseline_durations = baseline_map[baseline_root]

        if baseline_root in realtime_map:
            realtime_durations = realtime_map[baseline_root]
            del realtime_map[baseline_root]
        if not realtime_durations:
            res.extend(fill_baseline_durations(
                baseline_root, baseline_durations))
            continue

        for duration in baseline_durations:
            lookup[duration.operation] = duration.duration

        for realtime_duration in realtime_durations:
            if realtime_duration.operation in lookup:
                comparison = ComparisonResult(
                    root=baseline_root,
                    operation=realtime_duration.operation,
                    baseline=lookup[realtime_duration.operation],
                    realtime=realtime_duration.duration
                )
                if comparison.realtime-comparison.baseline > LATENCY_THRESHOLD:
                    comparison.suspected = True
                del lookup[realtime_duration.operation]
                res.append(comparison)
            else:
                comparison = ComparisonResult(
                    root=baseline_root,
                    operation=realtime_duration.operation,
                    realtime=realtime_duration.duration
                )
                res.append(comparison)
        if len(lookup) != 0:
            for i, (k, v) in enumerate(lookup.items()):
                comparison = ComparisonResult(
                    root=baseline_root,
                    operation=k,
                    baseline=v
                )
                res.append(comparison)

    if len(realtime_map) != 0:
        for realtime_root in realtime_map.keys():
            realtime_durations = realtime_map[realtime_root]
            res.extend(fill_realtime_durations(
                realtime_root,
                realtime_durations
            ))

    return res
