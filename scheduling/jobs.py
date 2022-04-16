import json
import time
from datetime import datetime

from config import state, ALPHA
from statistic.ks import ks_test_same_dist
from storage import retrieve_durations, retrieve_critical_path, store_json
from transform import extract_critical_path, extract_durations
from zipkin.helper import adjust_traces
from zipkin.models import AdjustedTrace, TraceParam
from zipkin.query import query_traces
from critical_path import compare_critical_path

from .constants import *


def get_baseline_traces() -> list[AdjustedTrace]:
    raw_traces = query_traces(TraceParam(
        endTs=round(time.time() * 1000),
        limit=TRACE_LIMIT,
        lookback=BASELINE_PROBE_TIME*1000
    ))
    traces = adjust_traces(raw_traces)
    return traces


def get_realtime_traces() -> list[AdjustedTrace]:
    raw_traces = query_traces(TraceParam(
        endTs=round(time.time() * 1000),
        limit=TRACE_LIMIT,
        lookback=REALTIME_CHECK_PERIOD*1000
    ))
    traces = adjust_traces(raw_traces)
    return traces


def retrieve_baseline_models():
    '''Query baseline traces from zipkin, transform into models
    , store in redis, change global state'''

    traces = get_baseline_traces()

    durations = extract_durations(traces)
    paths = extract_critical_path(traces)
    paths_json = [p.dict() for p in paths]

    curr_dt = datetime.now()
    timestamp = int(round(curr_dt.timestamp()))
    durations_key = f"baseline_durations-{timestamp}"
    paths_key = f"baseline_critical_path-{timestamp}"

    store_json(durations_key, json.dumps(durations))
    store_json(paths_key, json.dumps(paths_json))

    state.baselineReady = True
    state.baselineKey.duration = durations_key
    state.baselineKey.criticalPath = paths_key


def check_regression() -> bool:
    '''Check realtime regression by comparing realtime
    durations to baseline durations'''
    if not state.baselineReady:
        raise ValueError("Baseline not ready")

    realtime_traces = get_realtime_traces()
    realtime_durations = extract_durations(realtime_traces)
    baseline_durations = retrieve_durations(state.baselineKey.duration)

    test = ks_test_same_dist(realtime_durations, baseline_durations, ALPHA)

    return test


def perform_analysis():
    '''Perform Critical Path analysis + Correlation Analysis
    and store in redis'''
    if not state.baselineReady:
        raise ValueError("Baseline not ready")

    realtime_traces = get_realtime_traces()
    realtime_paths = extract_critical_path(realtime_traces)
    baseline_paths = retrieve_critical_path(state.baselineKey.criticalPath)

    result_paths = compare_critical_path(baseline_paths, realtime_paths)
    result_paths_json = [p.json() for p in result_paths]

    curr_dt = datetime.now()
    timestamp = int(round(curr_dt.timestamp()))
    result_paths_key = f"result_critical_path-{timestamp}"

    store_json(result_paths_key, json.dumps(result_paths_json))
    state.resultKey.criticalPath = result_paths_key
