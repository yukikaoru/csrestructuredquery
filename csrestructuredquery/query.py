from __future__ import annotations

import abc
import typing

if typing.TYPE_CHECKING:
    from csrestructuredquery.typing import Condition


class Query:
    def __init__(self, *conditions: Condition):
        ...


class LogicalCondition(metaclass=abc.ABCMeta):
    """論理条件文の基底クラス"""

    ...
