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
        if self.value is None:
            return ""
        if isinstance(self.value, datetime):
            return f"'{self.value.isoformat()}'"
        if isinstance(self.value, str):
            return f"'{self.value}'"
        return str(self.value)

    def __format__(self, format_spec) -> str:
        return str(self)

    def __bool__(self):
        return bool(str(self))

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return str(self) < str(other)
        raise TypeError

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return str(self) <= str(other)
        raise TypeError

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return str(self) == str(other)
        raise TypeError


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


@dataclasses.dataclass(frozen=True)
class Phrase(SpecializedOperator):
    field: str
    value: CsValue
    boost: int = dataclasses.field(default=0)

    @property
    def name(self) -> str:
        return "phrase"

    def query(self) -> str:
        q = f"({self.name} field={self.field}"
        if self.boost:
            q += f" boost={self.boost}"
        return f"{q} {ExpressionValue(self.value)})"


@dataclasses.dataclass(frozen=True)
class Prefix(SpecializedOperator):
    field: str
    value: CsValue
    boost: int = dataclasses.field(default=0)

    @property
    def name(self) -> str:
        return "prefix"

    def query(self) -> str:
        q = f"({self.name} field={self.field}"
        if self.boost:
            q += f" boost={self.boost}"
        return f"{q} {ExpressionValue(self.value)})"


@dataclasses.dataclass(frozen=True)
class Term(SpecializedOperator):
    field: str
    value: CsValue
    boost: int = dataclasses.field(default=0)

    @property
    def name(self) -> str:
        return "term"

    def query(self) -> str:
        q = f"({self.name} field={self.field}"
        if self.boost:
            q += f" boost={self.boost}"
        return f"{q} {ExpressionValue(self.value)})"


@dataclasses.dataclass(frozen=True)
class Range(SpecializedOperator):
    field: str
    min: typing.Optional[CsValue] = dataclasses.field(default=None)
    max: typing.Optional[CsValue] = dataclasses.field(default=None)
    boost: int = dataclasses.field(default=0)
    minbound: bool = dataclasses.field(default=True)
    maxbound: bool = dataclasses.field(default=False)

    def __post_init__(self):
        spec = RangeValueSpecification(min_=self.min, max_=self.max)
        if not spec.isvalidvalues():
            raise RangeArgumentError
        if not spec.isvalidrange():
            raise InvalidRangeError(min_=self.min, max_=self.max)

    @property
    def name(self) -> str:
        return "range"

    def query(self) -> str:
        q = f"({self.name} field={self.field}"
        if self.boost:
            q += f" boost={self.boost}"
        min_ = ExpressionValue(self.min)
        max_ = ExpressionValue(self.max)
        q += (
            " "
            + ("[" if min_ and self.minbound else "{")
            + f"{min_},{max_}"
            + ("]" if max_ and self.maxbound else "}")
            + ")"
        )
        return q


class RangeValueSpecification:
    def __init__(self, min_: CsValue, max_: CsValue):
        self.min = ExpressionValue(min_)
        self.max = ExpressionValue(max_)

    def isvalidvalues(self) -> bool:
        return bool(self.min or self.max)

    def isvalidrange(self) -> bool:
        return bool((self.max and self.min <= self.max) or (self.min and not self.max))


class RangeArgumentError(Exception):
    def __init__(self):
        self.message = "Cannot be set to None or empty string to both"


class InvalidRangeError(Exception):
    def __init__(self, min_: CsValue, max_: CsValue):
        self.message = f"Must be min less than max ({min_}, {max_})"
