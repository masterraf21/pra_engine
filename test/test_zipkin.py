import json
import random
import time
import unittest
from pathlib import Path
from timeit import default_timer as timer
from aioconsole import get_standard_streams


from config import settings
from src.utils.checking import *
from src.utils.testing import *
from src.zipkin import clock_skew, query
from src.zipkin import span_cleaner as cleaner
from src.zipkin import span_node
from src.zipkin import span_row as row
from src.zipkin import trace as trace_lib
from src.zipkin.helper import adjust_trace, adjust_traces
from src.zipkin.models import Annotation as An
from src.zipkin.models import Endpoint, Span, TraceParam

spanExample = {
    "A": 1,
    "B": 2,
    "C": 3
}


class TestAdjustedTrace(unittest.TestCase):
    def test_adjust_driver(self):
        file = 'kafka.json'
        trace = get_trace(file)
        nodes = adjust_trace(trace)
        write_json(nodes.json(), 'kafka_adjusted.json')

    def test_error_trace(self):
        id = '5e306b850f8297ff'
        trace = query.query_trace(id)
        adjusted = adjust_trace(trace)
        span = adjusted.spans
        if len(span) > 0:
            self.assertEqual("critical", span[0].errorType)
        write_json(adjusted.json(), 'error.json')

    def test_trace_clock_skew(self):
        file = '8.json'
        id = "4e863982c330afe0"
        trace = get_trace(file)
        self.assertEqual(8, len(trace))

        node = clock_skew.tree_corrected_for_clock_skew(trace)
        self.assertIsNotNone(node.span)
        self.assertEqual(id, node.span.traceId)
        self.assertEqual(4, len(node.children))

        # print(node.to_string())

    def test_adjusted_trace(self):
        # file = '8.json'
        id = "49e0cad3b6a96ffd"
        trace = query.query_trace(id)
        adjusted_trace = adjust_trace(trace)

        self.assertEqual(adjusted_trace.traceId, id)
        self.assertEqual(len(adjusted_trace.spans), 3)

        write_json(adjusted_trace.json(), "frontend.json")


class TestSpanCleaner(unittest.TestCase):
    def test_sort_annotations(self):
        l = [An(timestamp=12, value="tag"), An(
            timestamp=12, value="tag"), An(timestamp=3, value="3")]
        sorted = cleaner.sort_annotations(l)
        print(sorted)


class TestSpanRow(unittest.TestCase):
    def test_get_error_type_current(self):
        s1 = Span(id="a", traceId="a",
                  tags={
                      "err": "Halo error"
                  },
                  annotations=[An(timestamp=123, value="error")]
                  )
        err = "a"
        res = row.get_error_type(s1, err)
        self.assertEqual(res, "a")

    def test_get_error_type_transient(self):
        s1 = Span(id="a", traceId="a",
                  tags={
                      "err": "Halo error"
                  },
                  annotations=[]
                  )
        err = "a"
        res = row.get_error_type(s1, err)
        self.assertEqual(res, "transient")


class TestModel(unittest.TestCase):
    def test_enumerate_annotations(self):
        an = [An(timestamp=123, value="error"),
              An(timestamp=12, value="hiyas")]
        res = [i for i, j in enumerate(an) if j.value == "er"]
        print(res)

    def test_delete(self):
        s1 = Span(id="a", traceId="a",
                  localEndpoint=Endpoint(ipv4="123"),
                  shared=True)
        self.assertTrue(s1.shared)
        s1.shared = None
        self.assertIsNone(s1.shared)

    def test_spread(self):
        s1 = Span(id="a", traceId="a",
                  localEndpoint=Endpoint(ipv4="123"))
        s2 = Span(id="b", traceId="b", remoteEndpoint=Endpoint(
            ipv6="123", ipv4="111", port=123))
        ee = {**s1.localEndpoint.dict(), **s2.remoteEndpoint.dict()}
        e = Endpoint(**ee)
        print(ee)
        print(e)

    def test_empty_model(self):
        empty = Endpoint(serviceName="hey", port=1289)
        self.assertTrue(empty.serviceName)
        self.assertTrue(empty.port)
        self.assertFalse(empty.serviceName and empty.ipv4)

    def test_annotations_list(self):
        ann = An(
            timestamp=random.randint(1000000, 9999999999),
            value=id_generator()
        )

        l = [ann for _ in range(4)]
        d = dict(l)
        print(type(d))


class TestQuery(unittest.IsolatedAsyncioTestCase):
    def test_traces_sync(self):
        start = timer()

        now = round(time.time() * 1000)
        lb = 2*60*(60*1000)
        traces = query.query_traces_sync(TraceParam(
            lookback=lb,
            endTs=now,
            limit=100
        ))
        adjusted_traces = adjust_traces(traces)
        self.assertGreater(len(adjusted_traces), 10)
        adj_dict = [trace.dict() for trace in adjusted_traces]
        end = timer()
        print(end - start)
        write_json(json.dumps(adj_dict), "traces_sync.json")

    async def test_traces_async(self):
        start = timer()
        now = round(time.time() * 1000)
        lb = 2*60*(60*1000)
        traces = await query.query_traces(TraceParam(
            lookback=lb,
            endTs=now,
            limit=100
        ))
        adjusted_traces = adjust_traces(traces)
        print(len(adjusted_traces))
        self.assertGreater(len(adjusted_traces), 10)
        adj_dict = [trace.dict() for trace in adjusted_traces]
        end = timer()
        print(end - start, flush=True)
        write_json(json.dumps(adj_dict), "traces_async.json")

    def test_query_traces_empty(self):
        param = TraceParam()
        result = query.query_traces(param)

        self.assertEqual(type(result), list)
        if len(result) > 0:
            self.assertEqual(type(result[0]), list)
            if len(result[0]) > 0:
                span = result[0][0]
                self.assertEqual(type(span), Span)
                print(span.dict())

    def test_query_traces_1(self):
        param = TraceParam(
            serviceName="main"
        )
        result = query.query_traces(param)

        self.assertEqual(type(result), list)
        if len(result) > 0:
            self.assertEqual(type(result[0]), list)
            if len(result[0]) > 0:
                span = result[0][0]
                self.assertEqual(type(span), Span)
                print(span.dict())

    def test_query_services(self):
        result = query.query_services()
        print(result)
        self.assertEqual(type(result), list)
        if len(result) > 0:
            self.assertEqual(type(result[0]), str)

    def test_query_trace(self):
        id = "8cde39a41eef18e8"
        result = query.query_trace(id)

        span = result[0]
        self.assertEqual(id, span.traceId)
        span.id = "1"
        print(span.traceId)
        self.assertEqual(span.id, "1")

        self.assertEqual(type(result), list)
        if len(result) > 0:
            self.assertEqual(type(result[0]), Span)


class TestDynaconf(unittest.TestCase):
    def test_url(self):
        self.assertEqual(settings.src.zipkin_api,
                         "http://localhost:9411/src.zipkin/api/v2")


class TestsSpanNode(unittest.TestCase):

    def test_init_empty_node(self):
        span_node.SpanNode = span_node.span_node.SpanNode()
        self.assertEqual(type(span_node.SpanNode), span_node.SpanNode)

    def test_init_not_empty(self):
        node = span_node.SpanNode(spanExample)
        self.assertEqual(node.span, spanExample)
        self.assertEqual(node.parent, None)
        self.assertEqual(len(node.children), 0)

    def test_parenting(self):
        node = span_node.SpanNode(spanExample)
        nodeParent = span_node.SpanNode(spanExample)
        node.parent = nodeParent
        self.assertEqual(node.parent, nodeParent)

    def test_add_hild(self):
        node = span_node.SpanNode(spanExample)
        child = span_node.SpanNode(spanExample)
        node.add_child(child)
        self.assertEqual(len(node.children), 1)
        children = node.children
        self.assertEqual(children[0], child)
        self.assertEqual(child.parent, node)

    def test_add_child_exception(self):
        node = span_node.SpanNode(spanExample)
        child = span_node.SpanNode(spanExample)
        with self.assertRaises(ValueError):
            node.add_child(node)

    def test_queueRoot(self):
        node = span_node.SpanNode(spanExample)

    def test_to_string(self):
        node = span_node.SpanNode(spanExample)
        # print(node.toString())
        nodeStr = 'span_node.SpanNode({"A":1,"B":2,"C":3})'
        self.assertEqual(nodeStr, node.to_string())


class TestsSpanNodeBuilder(unittest.TestCase):
    pass
