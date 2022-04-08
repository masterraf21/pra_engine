from zipkin import span_node, clock_skew, utils, query, span_cleaner as cleaner, span_row as row, trace
import unittest
import random
import string
from config import settings
from zipkin.models import Span, TraceParam, Annotation as An, Endpoint, DependencyLink
import json
from pathlib import Path
from config import settings
from pydantic import parse_obj_as

spanExample = {
    "A": 1,
    "B": 2,
    "C": 3
}


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_json(file_name: str):
    path = Path(__file__).parent / f"json/{file_name}"
    with open(path, 'r') as f:
        j = json.loads(f.read())
        return j


def get_trace(file_name: str) -> list[Span]:
    j = get_json(file_name)
    trace = parse_obj_as(list[Span], j)
    return trace


class TestAdjustedTrace(unittest.TestCase):

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
        file = '8.json'
        id = "4e863982c330afe0"
        spans = get_trace(file)
        node = clock_skew.tree_corrected_for_clock_skew(spans)
        adjusted_trace = trace.detailed_trace_summary(node)
        self.assertEqual(adjusted_trace.traceId, id)


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


class TestQuery(unittest.TestCase):
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
        self.assertEqual(settings.zipkin_api,
                         "http://localhost:9411/zipkin/api/v2")


class TestSpanUtils(unittest.TestCase):
    def test_not_exist(self):
        x = {
            "a": 2, "b": 4, "c": 6, "d": None
        }
        t1 = utils.not_exist(x["a"])
        t2 = utils.not_exist(x["d"])
        # t3 = utils.not_exist(x[1])
        t3 = utils.key_exists(x, 1)
        self.assertEqual(t1, False)
        self.assertEqual(t2, True)
        self.assertEqual(t3, False)

    def test_exist(self):
        x = {
            "a": 2, "b": 4, "c": 6
        }
        t1 = utils.exist(x["a"])
        t2 = utils.exist(x["d"])
        self.assertEqual(t1, True)
        self.assertEqual(t2, False)


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
