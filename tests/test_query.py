from datetime import datetime

from csrestructuredquery.query import Query, And, Or, Not, Near, Phrase, Prefix, Term


def test_文字列型と日時型は引用符で括られる():
    q = Query(("foo", "hoge"), ("bar", 123), ("baz", datetime(2013, 1, 23, 12, 34, 56)))
    assert q.build() == "(and foo:'hoge' bar:123 baz:'2013-01-23T12:34:56')"


def test_AND論理式():
    expr = And(("foo", "hoge"), ("bar", 123))
    assert expr.query() == "(and foo:'hoge' bar:123)"


def test_OR論理式():
    expr = Or(("foo", "hoge"), ("bar", 123))
    assert expr.query() == "(or foo:'hoge' bar:123)"


def test_NOT論理式():
    expr = Not(("foo", "hoge"), ("bar", 123))
    assert expr.query() == "(not foo:'hoge' bar:123)"


def test_論理式は入れ子にできる():
    expr = And(("foo", "hoge"), Or(("bar", 123), Not(("baz", datetime(2013, 1, 23, 12, 34, 56)))))
    assert expr.query() == "(and foo:'hoge' (or bar:123 (not baz:'2013-01-23T12:34:56')))"


def test_near演算子():
    operator = Near(field="foo", value="hoge")
    assert operator.query() == "(near field=foo 'hoge')"
    operator = Near(field="foo", value="hoge", distance=2, boost=4)
    assert operator.query() == "(near field=foo distance=2 boost=4 'hoge')"


def test_phrase演算子():
    operator = Phrase(field="foo", value="hoge")
    assert operator.query() == "(phrase field=foo 'hoge')"
    operator = Phrase(field="foo", value="hoge", boost=4)
    assert operator.query() == "(phrase field=foo boost=4 'hoge')"


def test_prefix演算子():
    operator = Prefix(field="foo", value="hoge")
    assert operator.query() == "(prefix field=foo 'hoge')"
    operator = Prefix(field="foo", value="hoge", boost=4)
    assert operator.query() == "(prefix field=foo boost=4 'hoge')"


def test_term演算子():
    operator = Term(field="foo", value="hoge")
    assert operator.query() == "(term field=foo 'hoge')"
    operator = Term(field="foo", value="hoge", boost=4)
    assert operator.query() == "(term field=foo boost=4 'hoge')"
