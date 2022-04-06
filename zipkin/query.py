import requests


def query_traces(param: dict) -> list[dict]:
    req = requests.get()


def query_trace(id: str) -> dict:
    pass


def query_trace_many(ids: list[str]) -> dict:
    pass


def query_span_names(service_name: str) -> list[str]:
    pass


def query_dependencies(end_ts: int, lokback: int) -> list[dict]:
    pass


def query_services() -> list[str]:
    pass
