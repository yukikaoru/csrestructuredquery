from __future__ import annotations

import abc
import typing
from dataclasses import dataclass
from datetime import datetime

if typing.TYPE_CHECKING:
    from csrestructuredquery.typing import Expression, CsValue


class Query:
    def __init__(self, *expressions: Expression):
        self.__expressions = expressions

    def build(self) -> str:
        return And(*self.__expressions).query()


@dataclass(frozen=True)
class ExpressionValue:
    value: CsValue

    def __str__(self) -> str:
        return format(self.value)

    def __format__(self, format_spec) -> str:
        if self.value is None:
            return ""
        if isinstance(self.value, datetime):
            return f"'{self.value.isoformat()}'"
        if isinstance(self.value, str):
            return f"'{self.value}'"
        return str(self.value)


class LogicalExpression(metaclass=abc.ABCMeta):
    """論理式の基底クラス"""

    name: str

    def __init__(self, *expressions: Expression):
        self.__expressions = expressions

    def query(self) -> str:
        q = f"({self.name}"
        for expr in self.__expressions:
            if isinstance(expr, tuple):
                q += f" {expr[0]}:{ExpressionValue(expr[1])}"
            else:
                q += f" {expr.query()}"
        q += ")"
        return q


class And(LogicalExpression):
    name = "and"


class Or(LogicalExpression):
    name = "or"


class Not(LogicalExpression):
    name = "not"
