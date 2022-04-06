import json
from .utils import *
from .span_cleaner import *
from collections import deque
from typing import Callable


class SpanNode:
    def __init__(self, span: dict = None) -> None:
        self._parent: 'SpanNode' = None
        self._span = span
        self._children: list['SpanNode'] = []

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        self._parent = new_parent

    @property
    def span(self):
        return self._span

    @span.setter
    def span(self, span):
        if not span:
            raise ValueError("Span Undefined")
        self._span = span

    @property
    def children(self):
        return self._children

    def add_child(self, child: 'SpanNode'):
        if not child:
            raise ValueError("Child was Undefined")
        if child == self:
            raise ValueError("Circular dependency detected")
        child.parent = self
        self._children.append(child)

    def traverse(self, callback: Callable):
        queue = self.queue_root_most_spans()
        while len(queue) > 0:
            current = queue.popleft()

            callback(current.span)

            children = current.children
            for i in range(len(children)):
                queue.append(children[i])

    def queue_root_most_spans(self) -> deque['SpanNode']:
        queue = deque()
        if self.span == None:
            for child in self.children:
                queue.append(child)
        else:
            queue.append(self)

        if len(queue) == 0:
            raise ValueError("Trace was Empty")

        return queue

    def to_string(self) -> str:
        if self.span:
            return f"SpanNode({json.dumps(self.span, separators=(',', ':'))})"

        return "SpanNode()"


class SpanNodeBuilder:
    def __init__(self, debug=False) -> None:
        self._debug = debug
        self._rootSpan = None
        self._keyToNode = {}
        self._spanToParent = {}

    def _index(self, span: dict):
        idKey, parentKey = None, None

        if span["shared"]:
            idKey = key_string(span["id"], True, span["localEndpoint"])
            parentKey = span["id"]
        else:
            idKey = span["id"]
            parentKey = span["parentId"]

        self._spanToParent[idKey] = parentKey

    def _process(self, span: dict):
        endpoint = span["localEndpoint"]
        key = key_string(span["id"], span["shared"], span["localEndpoint"])
        noEndpointKey = key_string(
            span["id", span["shared"]]) if endpoint else key

        parent = None
        if span["shared"]:
            parent = span["id"]
        elif span["parentId"]:
            parent = key_string(span["parentId"], True, endpoint)
            if self._spanToParent[parent]:
                self._spanToParent[noEndpointKey] = parent
            else:
                parent = span["parentId"]
        elif self._rootSpan:
            if self._debug:
                prefix = "attributing span missing parent to root"
                print(
                    f'{prefix}: traceId={span["traceId"]}, rootId={self._rootSpan["span"]["id"]}, id={span["id"]}')

        node = SpanNode(span)

        if not parent and not self._rootSpan:
            self._rootSpan = node
            del self._spanToParent[noEndpointKey]
        elif span["shared"]:
            self._keyToNode[key] = node
            self._keyToNode[noEndpointKey] = node
        else:
            self._keyToNode[noEndpointKey] = node

    def build(self, spans: list[dict]):
        if len(spans) == 0:
            raise ValueError("Trace was empty")

        cleaned = merge_v2_by_id(spans)
        length = len(cleaned)
        # TODO: Potential Bug
        traceId_many = [sub['traceId'] for sub in cleaned]
        traceId = None
        if traceId_many:
            traceId = traceId_many[0]
        if self._debug:
            print(f'building trace tree: traceId={traceId}')

        for i in range(length):
            self._index(cleaned[i])

        for i in range(length):
            self._process(cleaned[i])

        if not self._rootSpan:
            if self._debug:
                print(
                    f'subtituting dummy node for missing root span: traceId={traceId}'
                )
            self._rootSpan = SpanNode()

        for key in self._spanToParent:
            child = self._keyToNode[key]
            parent = self._keyToNode[self._spanToParent[key]]

            # TODO: Potential Bug
            if not parent:
                self._rootSpan.add_child(child)
            else:
                parent.add_child(child)

        sort_tree_by_timestamp(self._rootSpan)

        return self._rootSpan


def sort_tree_by_timestamp(root: SpanNode):
    queue = deque()
    queue.append(root)

    while len(queue) > 0:
        current = queue.popleft()

        sort_children(current)

        children = current.children
        for i in range(len(children)):
            queue.append(children[i])


def sort_children(node: SpanNode):
    if len(node.children) > 0:
        sorted(node.children, cmp_to_key=node_by_timestamp)
