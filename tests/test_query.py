from datetime import datetime

from csrestructuredquery.query import Query, And, Or


def test_文字列型と日時型は引用符で括られる():
    q = Query(("foo", "hoge"), ("bar", 123), ("baz", datetime(2013, 1, 23, 12, 34, 56)))
    assert q.build() == "(and foo:'hoge' bar:123 baz:'2013-01-23T12:34:56')"


def test_AND論理演算子():
    expr = And(("foo", "hoge"), ("bar", 123))
    assert expr.query() == "(and foo:'hoge' bar:123)"


def test_OR論理演算子():
    expr = Or(("foo", "hoge"), ("bar", 123))
    assert expr.query() == "(or foo:'hoge' bar:123)"
