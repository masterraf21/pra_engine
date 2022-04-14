from typing import Optional
from .models import CriticalPath, ComparisonResult, PathDuration
from .constants import LATENCY_THRESHOLD


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
