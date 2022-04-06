from functools import cmp_to_key
from .utils import *
from .trace_constants import ConstantNames


def get_error_type(span: dict, current_error_type):
    if current_error_type == "critical":
        return current_error_type
    # TODO: Exsception
    if span["tags"]["error"]:
        return "critical"
    try:
        res = [i for i, j in enumerate(
            span["annotations"]) if j["value"] == "error"]
    except ValueError:
        return "transient"

    return current_error_type


def get_service_name(endpoint: dict):
    return endpoint["serviceName"] if endpoint else None


def maybe_push_service_name(service_names: list, service_name):
    if not service_name:
        return
    if service_names.count(service_name) == 0:
        service_names.append(service_name)


def format_endpoint(endpoint):
    if not endpoint:
        return None
    ipv4, ipv6, port, serviceName = (
        endpoint["ipv4"],
        endpoint["ipv6"],
        endpoint["port"],
        endpoint["serviceName"],
    )
    if ipv4 or ipv6:
        ip = f"[{ipv6}]" if ipv6 else ipv4
        port_string = f'"{port}' if port else ""
        serviceName_string = f"({port})" if port else ""
        return ip + port_string + serviceName_string
    return serviceName or ""


def to_annotation_row(a, local_formatted, is_derived: bool = False):
    res = {
        "isDerived": is_derived,
        "value": ConstantNames[a["value"]] or a["value"],
        "timestamp": a["timestamp"],
    }
    if local_formatted:
        res["endpoint"] = local_formatted
    return res


def parse_annotations_row(span: dict):
    local_formatted = format_endpoint(span["localEndpoint"]) or None

    startTs = span["timestamp"] or 0
    endTs = startTs + span["duration"] if startTs and span["duration"] else 0
    msTs = 0
    wsTs = 0
    wrTs = 0
    mrTs = 0

    begin, end = None, None
    kind = span["kind"]

    annotations_to_add = []
    for a in span["annotations"]:
        match a["value"]:
            case "cs":
                kind = "CLIENT"
                if a["timestamp"] <= startTs:
                    startTs = a["timestamp"]
                else:
                    annotations_to_add.append(a)
            case "sr":
                kind = "SERVER"
                if a["timestamp"] <= startTs:
                    startTs = a["timestamp"]
                else:
                    annotations_to_add.append(a)
            case "ss":
                kind = "SERVER"
                if a["timestamp"] >= endTs:
                    endTs = a["timestamp"]
                else:
                    annotations_to_add.append(a)
            case "cr":
                kind = "CLIENT"
                if a["timestamp"] >= endTs:
                    endTs = a["timestamp"]
                else:
                    annotations_to_add.append(a)
            case "ms":
                kind = "PRODUCER"
                msTs = a["timestamp"]
            case "mr":
                kind = "PRODUCER"
                mrTs = a["timestamp"]
            case "ws":
                wsTs = a["timestamp"]
            case "wr":
                wrTs = a["timestamp"]
            case _:
                annotations_to_add.append(a)

    match kind:
        case "CLIENT":
            begin = "Client Start"
            end = "Client Finish"
        case "SERVER":
            begin = "Server Start"
            end = "Server Finish"
        case "PRODUCER":
            begin = "Producer Start"
            end = "Producer Finish"
            if startTs == 0 or (msTs != 0 and msTs < startTs):
                startTs = msTs
                msTs = 0
            if endTs == 0 or (wrTs != 0 and wrTs < startTs):
                endTs = wsTs
                wsTs = 0
        case "CONSUMER":
            if startTs == 0 or (wrTs != 0 and wrTs < startTs):
                startTs = wrTs
                wrTs = 0
            if endTs == 0 or (mrTs != 0 and mrTs > endTs):
                endTs = mrTs
                mrTs = 0
            if endTs != 0 or wrTs != 0:
                begin = "Consumer Start"
                end = "Consumer Finish"
            else:
                begin = "Consumer Start"

    if msTs:
        annotations_to_add.append({"timestamp": msTs, "value": 'ms'})
    if wsTs:
        annotations_to_add.append({"timestamp": wsTs, "value": "ws"})
    if wrTs:
        annotations_to_add.append({"timestamp": wrTs, "value": "wr"})
    if mrTs:
        annotations_to_add.append({"timestamp": mrTs, "value": "mr"})

    begin_annotation = startTs and begin
    end_annotation = endTs and end

    annotations = []

    if begin_annotation:
        annotations.append(
            to_annotation_row({
                "value": begin,
                "timestamp": startTs
            },
                local_formatted,
                True)
        )

    for a in annotations_to_add:
        if begin_annotation and a["value"] == begin:
            return
        if end_annotation and a["value"] == end:
            return
        annotations_to_add.append(to_annotation_row(a, local_formatted))

    if end_annotation:
        annotations.append(
            to_annotation_row({
                "value": end,
                "timestamp": endTs
            },
                local_formatted,
                True)
        )

    return annotations


def parse_tag_rows(span: dict):
    local_formatted = format_endpoint(span["localEndpoint"]) or None

    tag_rows = []
    keys = span["tags"].keys() if type(span["taggs"]) == dict else []
    if len(keys) > 0:
        for key in keys:
            tag_row = {
                "key": ConstantNames[key] or key,
                "value": span["tags"][key]
            }
            if local_formatted:
                tag_row["endpoints"] = [local_formatted]
            tag_rows.append(tag_row)

    if not span["kind"] and len(
            span["annotations"]) == 0 and local_formatted and len(keys) == 0:
        tag_rows.push({
            "key": "Local Address",
            "value": local_formatted
        })

    addr = None
    match span["kind"]:
        case "CLIENT":
            addr = "Server Address"
        case "SERVER":
            addr = "Client Address"
        case "PRODUCER":
            addr = "Broker Address"
        case "CONSUNER":
            addr = "Broker Address"

    if span["remoteEndpoint"]:
        tag_rows.append({
            "key": addr or "Server Address",
            "value": format_endpoint(span["remoteEndpoint"])
        })

    return tag_rows


def maybe_push_annotation(annotations: list[dict], a: dict):
    try:
        res = [i for i, b in enumerate(
            annotations) if a["timestamp"] == b["timestamp"] and a["value"] == b["value"]]
    except ValueError:
        annotations.append(a)


def maybe_push_tag(tags: list[dict], a: dict):
    same_key_and_value = list(filter(
        lambda b: b["key"] == a["key"] and a["value"] == b["value"], tags))

    if len(same_key_and_value) == 0:
        tags.append(a)
        return

    if len(a["endpoints"] or []) == 0:
        return

    for t in same_key_and_value:
        if not key_exists(t, "endpoints"):
            t["endpoints"] = []
        if key_exists(a, "endpoints") and check_list(a["endpoints"]):
            for endpoint in a["endpoints"]:
                if t["endpoints"].count(endpoint) == 0:
                    t["endpoints"].append(endpoint)


def new_span_row(spans_to_merge: list[dict], is_leaf_span: bool) -> dict:
    first = spans_to_merge[0]
    res = {
        "spanId": first["id"],
        "serviceNames": [],
        "annotations": [],
        "tags": [],
        "errorType": None,
    }

    shared_timestamp = None
    shared_duration = None
    for next in spans_to_merge:
        if next["parentId"]:
            res["parentId"] = next["parentId"]
        if next["name"] and (not res["spanName"] or next["kind"] == "SERVER"):
            res["spanName"] = next["name"]

        if next["shared"]:
            if not shared_timestamp:
                shared_timestamp = next["timestamp"]
            if not shared_duration:
                shared_duration = next["duration"]
        else:
            if not res["timestamp"] and next["timestamp"]:
                res["timestamp"] = next["timestamp"]
            if not res["duration"] and next["duration"]:
                res["duration"] = next["duration"]

        next_local_service_name = get_service_name(next["localEndpoint"])
        next_remote_service_name = get_service_name(next["remoteEndpoint"])

        if next_local_service_name and next["kind"] == "SERVER":
            res["serviceName"] = next_local_service_name
        elif (
            is_leaf_span
            and next_remote_service_name
            and next["kind"] == "CLIENT"
            and not res["serviceName"]
        ):
            res["serviceName"] = next_remote_service_name
        elif next_local_service_name and not res["serviceName"]:
            res["serviceName"] = next_local_service_name

        maybe_push_service_name(res["serviceNames"], next_local_service_name)
        maybe_push_service_name(res["serviceNames"], next_remote_service_name)

        for a in parse_annotations_row(next):
            maybe_push_annotation(res["annotations"], a)

        for tag in parse_tag_rows(next):
            maybe_push_tag(res["tags"], tag)

        res["errorType"] = get_error_type(next, res["errorType"])

        if next["debug"]:
            res["debug"] = True

        if not key_exists(res, "timestamps") and shared_timestamp:
            res["timestamp"] = shared_timestamp
        if not key_exists(res, "duration") and shared_duration:
            res["duration"] = shared_duration

        if not_exist(res["duration"]):
            res["duration"] = 0
        if not_exist(res["spanName"]):
            res["spanName"] = 'unknown'
        if not_exist(res["serviceName"]):
            res["serviceName"] = 'unknown'

        for a in res["annotations"]:
            if not_exist(a["endpoint"]):
                a["endpoint"] = 'unknown'

        res["serviceNames"].sort()
        sorted(res["annotations"], key=cmp_to_key(
            lambda a, b: a["timestamp"] - b["timestamp"]
        ))

        return
