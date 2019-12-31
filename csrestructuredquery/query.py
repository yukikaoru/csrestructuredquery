from __future__ import annotations

import abc
import dataclasses
import typing
from datetime import datetime

if typing.TYPE_CHECKING:
    from csrestructuredquery.typing import Expression, CsValue


class Query:
    def __init__(self, *expressions: Expression):
        self.__expressions = expressions

    def build(self) -> str:
        return And(*self.__expressions).query()


@dataclasses.dataclass(frozen=True)
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

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

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
    @property
    def name(self) -> str:
        return "and"


class Or(LogicalExpression):
    @property
    def name(self) -> str:
        return "or"


class Not(LogicalExpression):
    @property
    def name(self) -> str:
        return "not"


class SpecializedOperator(metaclass=abc.ABCMeta):
    """専門演算子の基底クラス"""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def query(self) -> str:
        pass


@dataclasses.dataclass(frozen=True)
class Near(SpecializedOperator):
    field: str
    value: CsValue
    distance: int = dataclasses.field(default=0)
    boost: int = dataclasses.field(default=0)

    @property
    def name(self) -> str:
        return "near"

    def query(self) -> str:
        q = f"({self.name} field={self.field}"
        if self.distance:
            q += f" distance={self.distance}"
        if self.boost:
            q += f" boost={self.boost}"
        return f"{q} {ExpressionValue(self.value)})"
