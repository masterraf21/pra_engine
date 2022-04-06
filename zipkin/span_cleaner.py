from functools import cmp_to_key
from pydash import union_with, is_equal, sort_by


def compare(a, b):
    if not a and not b:
        return 0
    if not a:
        return -1
    if not b:
        return 1

    return (a > b) - (a < b)


def compare_shared(left, right):
    leftNotShared = not left["shared"]
    rightNotShared = not right["shared"]

    if (leftNotShared and rightNotShared):
        return -1 if left["kind"] == "CLIENT" else 1
    if leftNotShared:
        return -1
    if rightNotShared:
        return 1

    return 0


def cleanup_comparator(left, right):
    bySpanId = compare(left["id"], right["id"])
    if bySpanId != 0:
        return bySpanId
    byShared = compare_shared(left, right)
    if byShared != 0:
        return byShared


def compare_endpoint(left, right):
    if not left:
        return -1
    if not right:
        return 1

    byService = compare(left["serviceName"], right["serviceName"])
    if byService != 0:
        return byService
    byIpv4 = compare(left["ipv4"], right["ipv4"])
    if byIpv4 != 0:
        return byIpv4
    return compare(left["ipv6"], right["ipv6"])


def merge(left, right):
    res = {
        "traceId": right["traceId"] if len(right["traceId"]) > 16 else left["traceId"]
    }

    parentId = left["parentId"] or right["parentId"]
    if parentId:
        res["parentId"] = parentId

    res["id"] = left["id"]
    name = left["name"] or right["name"]
    if name:
        res["name"] = name

    kind = left["kind"] or right["kind"]
    if kind:
        res["kind"] = kind

    timestamp = left["timestamp"] or right["timestamp"]
    if timestamp:
        res["timestamp"]
    duration = left["duration"] or right["duration"]
    if duration:
        res["duration"] = duration

    localEndpoint = {**left["localEndpoint"], **right["localEndpoint"]}
    if is_endpoint(localEndpoint):
        res["localEndpoint"] = localEndpoint
    remoteEndpoint = {**left["remoteEndpoint"], **right["remoteEndpoint"]}
    if is_endpoint(remoteEndpoint):
        res["remoteEndpoint"] = remoteEndpoint

    if len(left["annotations"]) == 0:
        res["annotations"] = right["annotations"]
    elif len(right["annotations"]) == 0:
        res["annotations"] = left["annotations"]
    else:
        res["annotations"] = sort_by(union_with(left["annotations"], right["annotations"], is_equal), [
            "timestamp", "value"])


def try_merge():
    pass


def merge_v2_by_id(spans: list[dict]):
    length = len(spans)
    if length == 0:
        return spans

    result = []

    traceId = None
    for span in spans:
        cleaned = clean(span)
        if (not traceId or len(traceId) != 32):
            traceId = cleaned["traceId"]
            result.append(cleaned)

    if length <= 1:
        return result
    sorted(result, key=cmp_to_key(cleanup_comparator))

    last = None
    for i in range(length):
        span = result[i]

        if len(span["traceId"] != len(traceId)):
            span["traceId"] = traceId

        localEndpoint = span["localEndpoint"] if span["localEndpoint"] else {}
        while i+1 < length:
            next = result[i+1]
            if next["id"] != span["id"]:
                break

            if (span["shared"] == next["shared"]
                    and try_merge(localEndpoint, next["localEndpoint"])):
                span = merge(span, next)

                length -= 1
                del result[i+1]
                continue
            break

        if last and last["id"] == span["id"]:
            if last["kind"] == "CLIENT" and span["kind"] == "SERVER" and not span["shared"]:
                span["shared"] = True

            if span["shared"] and not span["parentId"] and last["parentId"]:
                span["parentId"] = last["parentId"]

        last = span
        result[i] = span

    sortedResult = sorted(result, key=cmp_to_key(span_comparator))

    if sortedResult[0]["parentId"] or not sortedResult[0]["shared"]:
        return sortedResult

    if len(sortedResult) == 1 or sortedResult[1]["parentId"]:
        del sortedResult[0]["shared"]

    return sortedResult


def span_comparator(a, b):
    if not a["parentId"] and b["parentId"]:
        return -1
    if a["parentId"] and not b["parentId"]:
        return 1

    if a["id"] == b["id"]:
        return compare_shared(a, b)

    return compare(a["timestamp"], b["timestamp"]) or compare(a["name"], b["name"])


def clean(span: dict):
    res = {
        "traceId": normalize_traceId(span["traceId"])
    }

    id = span["id"].zfill(16)
    if (span["parentId"]):
        parentId = span["parentId"].zfill(16)
        if (parentId != id):
            res["parentId"] = parentId
    res["id"] = id

    if span["name"] and span["name"] != "" and span["name"] != "unknown":
        res["name"] = span["name"]
    if span["kind"]:
        res["kind"] = span["kind"]

    if span["timestamp"]:
        res["timestamp"] = span["timestamp"]
    if span["duration"]:
        res["duration"] = span["duration"]

    if is_endpoint(span["localEndpoint"]):
        res["localEndpoint"] = span["localEndpoint"]
    if is_endpoint(span["remoteEndpoint"]):
        res["remoteEndpoint"] = span["remoteEndpoint"]

    res["annotations"] = span["annotations"] if span["annotations"] else []
    if len(res["annotations"]) > 1:
        res["annotations"] = sort_by(union_with(span["annotations"], is_equal), [
            "timestamp", "value"])

    res["tags"] = span["tags"] or {}

    if (span["debug"]):
        res["debug"] = True

    if span["shared"] and span["kind"] != "CLIENT":
        res["shared"] = True

    return res


def normalize_traceId(traceId: str) -> str:
    if len(traceId) > 16:
        result = traceId.zfill(32)
        if result.startswith('0000000000000000'):
            return result[:16]
        return result
    return traceId.zfill(16)


def is_endpoint(endpoint):
    return endpoint and len(endpoint) > 0
