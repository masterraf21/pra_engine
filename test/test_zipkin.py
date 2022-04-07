from zipkin import SpanNode, SpanNodeBuilder, utils, query
import unittest
from config import settings
from zipkin.models import Span, TraceParam

spanExample = {
    "A": 1,
    "B": 2,
    "C": 3
}


class TestQuery(unittest.TestCase):
    def test_query_traces(self):
        param = TraceParam()
        result = query.query_traces(param)

        self.assertEqual(type(result), list)
        if len(result) > 0:
            self.assertEqual(type(result[0]), list)
            if len(result[0]) > 0:
                span = result[0][0]
                self.assertEqual(type(span), Span)
                print(span.dict())

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


class TestSpanNode(unittest.TestCase):

    def test_init_empty_node(self):
        spanNode = SpanNode()
        self.assertEqual(type(spanNode), SpanNode)

    def test_init_not_empty(self):
        node = SpanNode(spanExample)
        self.assertEqual(node.span, spanExample)
        self.assertEqual(node.parent, None)
        self.assertEqual(len(node.children), 0)

    def test_parenting(self):
        node = SpanNode(spanExample)
        nodeParent = SpanNode(spanExample)
        node.parent = nodeParent
        self.assertEqual(node.parent, nodeParent)

    def test_add_hild(self):
        node = SpanNode(spanExample)
        child = SpanNode(spanExample)
        node.add_child(child)
        self.assertEqual(len(node.children), 1)
        children = node.children
        self.assertEqual(children[0], child)
        self.assertEqual(child.parent, node)

    def test_add_child_exception(self):
        node = SpanNode(spanExample)
        child = SpanNode(spanExample)
        with self.assertRaises(ValueError):
            node.add_child(node)

    def test_queueRoot(self):
        node = SpanNode(spanExample)

    def test_to_string(self):
        node = SpanNode(spanExample)
        # print(node.toString())
        nodeStr = 'SpanNode({"A":1,"B":2,"C":3})'
        self.assertEqual(nodeStr, node.to_string())


class TestSpanNodeBuilder(unittest.TestCase):
    pass
