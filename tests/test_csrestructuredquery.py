from datetime import datetime

from csrestructuredquery.query import Query


def test_文字列型と日時型は引用符で括られる():
    q = Query(("foo", "hoge"), ("bar", 123), ("baz", datetime(2013, 1, 23)))
    assert str(q) == "(and foo:'hoge' bar:123 baz:'1923-09-01T11:58:32.123456')"
