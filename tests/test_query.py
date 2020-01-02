from datetime import datetime

import pytest

from csrestructuredquery.query import (
    Query,
    And,
    Or,
    Not,
    Near,
    Phrase,
    Prefix,
    Term,
    Range,
    RangeArgumentError,
    InvalidRangeError,
)


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


def test_range演算子はデフォルトでmin以上max未満となる():
    operator = Range(field="foo", min=12, max=34)
    assert operator.query() == "(range field=foo [12,34})"
    operator = Range(field="foo", min=12, max=34, boost=4)
    assert operator.query() == "(range field=foo boost=4 [12,34})"


def test_range演算子においてminはNoneを許容する():
    operator = Range(field="foo", min=None, max=34)
    assert operator.query() == "(range field=foo {,34})"
    operator = Range(field="foo", max=34)
    assert operator.query() == "(range field=foo {,34})"


def test_range演算子においてmaxはNoneを許容する():
    operator = Range(field="foo", min=12, max=None)
    assert operator.query() == "(range field=foo [12,})"
    operator = Range(field="foo", min=12)
    assert operator.query() == "(range field=foo [12,})"


def test_range演算子においてminとmaxの両方がNoneだった場合にRangeArgumentErrorが発生する():
    with pytest.raises(RangeArgumentError):
        Range(field="foo", min=None, max=None)


def test_range演算子においてminがmaxより大きかった場合にInvalidRangeErrorが発生する():
    with pytest.raises(InvalidRangeError):
        Range(field="foo", min=34, max=12)


def test_range演算子は比較演算子の境界を含むかどうかを選択可能():
    operator = Range(field="foo", min=12, max=34, minbound=True, maxbound=True)
    assert operator.query() == "(range field=foo [12,34])"
    operator = Range(field="foo", min=12, max=34, minbound=False, maxbound=False)
    assert operator.query() == "(range field=foo {12,34})"
    operator = Range(field="foo", max=34, minbound=True)
    assert operator.query() == "(range field=foo {,34})"
    operator = Range(field="foo", min=12, maxbound=True)
    assert operator.query() == "(range field=foo [12,})"
