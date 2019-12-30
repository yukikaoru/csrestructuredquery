from datetime import datetime

from csrestructuredquery.query import Query


def test_文字列型と日時型は引用符で括られる():
    q = Query(("foo", "hoge"), ("bar", 123), ("baz", datetime(2013, 1, 23, 12, 34, 56)))
    assert q.build() == "(and foo:'hoge' bar:123 baz:'2013-01-23T12:34:56')"
