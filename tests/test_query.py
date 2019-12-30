from datetime import datetime

from csrestructuredquery.query import Query, And, Or, Not


def test_文字列型と日時型は引用符で括られる():
    q = Query(("foo", "hoge"), ("bar", 123), ("baz", datetime(2013, 1, 23, 12, 34, 56)))
    assert q.build() == "(and foo:'hoge' bar:123 baz:'2013-01-23T12:34:56')"


def test_AND論理演算子():
    expr = And(("foo", "hoge"), ("bar", 123))
    assert expr.query() == "(and foo:'hoge' bar:123)"


def test_OR論理演算子():
    expr = Or(("foo", "hoge"), ("bar", 123))
    assert expr.query() == "(or foo:'hoge' bar:123)"


def test_NOT論理演算子():
    expr = Not(("foo", "hoge"), ("bar", 123))
    assert expr.query() == "(not foo:'hoge' bar:123)"


def test_論理演算子は入れ子にできる():
    expr = And(("foo", "hoge"), Or(("bar", 123), Not(("baz", datetime(2013, 1, 23, 12, 34, 56)))))
    assert expr.query() == "(and foo:'hoge' (or bar:123 (not baz:'2013-01-23T12:34:56')))"
