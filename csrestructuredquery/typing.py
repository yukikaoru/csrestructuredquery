from datetime import datetime
from typing import Tuple, Union

from csrestructuredquery.query import LogicalExpression

CsValue = Union[int, str, datetime]
Expression = Union[LogicalExpression, Tuple]
