from abc import abstractmethod
import functools as f
import operator as op
from typing import Any, Generic, Iterable, Sequence, TypeAlias, TypeVar, overload
import typing
import pandas as pd

class _Constraint():
  @abstractmethod
  def __contains__(self, obj) -> bool:
    pass

  @abstractmethod
  def mask(self, df: pd.DataFrame|pd.Series) -> pd.Series:
    pass

class _ContainerConstraint(_Constraint):
  @overload
  def __init__(self, cs: Iterable[_Constraint]): ...
  @overload
  def __init__(self, *cs: _Constraint): ...
  def __init__(self, *cs): # pyright: ignore
    if len(cs) == 0 or isinstance(cs[0], _Constraint):
      self.cs = typing.cast(Iterable[_Constraint], cs)
    else:
      assert len(cs) == 1
      assert isinstance(cs[0], Iterable)
      self.cs = typing.cast(Iterable[_Constraint], cs[0])
  
class _NotConstraint(_Constraint):
  def __init__(self, c: _Constraint):
    self.c = c

  def __contains__(self, obj):
    return obj in self.c

  def mask(self, df):
    return ~self.c.mask(df)
    
class _OrConstraint(_ContainerConstraint):
  def __init__(self, *cs):
    super().__init__(*cs)

  def __contains__(self, obj):
    return any(obj in c for c in self.cs)

  def mask(self, df):
    return f.reduce(op.or_, (c.mask(df) for c in self.cs), pd.Series([False]*df.shape[0], index=df.index))
  
class _AndConstraint(_ContainerConstraint):
  def __init__(self, *cs):
    super().__init__(*cs)

  def __contains__(self, obj):
    return all(obj in c for c in self.cs)

  def mask(self, df):
    return f.reduce(op.and_, (c.mask(df) for c in self.cs), pd.Series([True]*df.shape[0], index=df.index))
  
class _EqConstraint(_Constraint):
  def __init__(self, obj: Any):
    self.obj = obj

  def __contains__(self, obj):
    return obj == self.obj

  def mask(self, df):
    return df == self.obj
  
class _RangeConstraint(_Constraint):
  def __init__(self, lb: None|int|float, ub: None|int|float,
               lb_strict: bool = False,
               ub_strict: bool = True):
    self.lb = lb
    self.ub = ub
    self.lb_strict = lb_strict
    self.ub_strict = ub_strict

  def __contains__(self, obj):
    return isinstance(obj, (int, float)) \
      and ((self.lb is None) or ((self.lb < obj) if self.lb_strict else (self.lb <= obj))) \
      and ((self.ub is None) or ((self.ub > obj) if self.ub_strict else (self.ub >= obj)))

  def mask(self, df):
    m = pd.Series([True]*df.shape[0], index=df.index)
    if self.lb is not None:
      m &= (self.lb < df) if self.lb_strict else (self.lb <= df)
    if self.ub is not None:
      m &= (self.ub > df) if self.ub_strict else (self.ub >= df)
    return m

_T = TypeVar('_T')
class NOT(Generic[_T]):
  __match_args__ = ("thing",)
  def __init__(self, thing: _T):
    self.thing = thing

class OR(Generic[_T]):
  __match_args__ = ("things",)
  def __init__(self, *things: _T):
    self.things = things

class AND(Generic[_T]):
  __match_args__ = ("things",)
  def __init__(self, *things: _T):
    self.things = things

class RANGE:
  __match_args__ = ("lb", "ub", "lb_strict", "ub_strict")
  def __init__(self, lb: None|int|float, ub: None|int|float,
               lb_strict: bool = False,
               ub_strict: bool = True):
    self.lb = lb
    self.ub = ub
    self.lb_strict = lb_strict
    self.ub_strict = ub_strict

NumConstraint: TypeAlias = int | float   \
  | tuple[None|int|float,None|int|float] \
  | RANGE                                \
  | Sequence['NumConstraint']            \
  | NOT['NumConstraint']                 \
  | OR['NumConstraint']                  \
  | AND['NumConstraint']

def parse_NumConstraint(c: NumConstraint) -> _Constraint:
  match c:
    case int() | float():
      return _EqConstraint(c)
    case ((None | int() | float()) as lb,
          (None | int() | float()) as ub):
      return _RangeConstraint(lb, ub)
    case RANGE(lb, ub, lb_strict, ub_strict):
      return _RangeConstraint(lb, ub, lb_strict, ub_strict)
    case NOT(c):
      return _NotConstraint(parse_NumConstraint(c))
    case AND(cs):
      return _AndConstraint(map(parse_NumConstraint, cs))
    case OR(cs) | [*cs]:
      return _OrConstraint(map(parse_NumConstraint, cs))
  raise Exception(f"Invalid float constraint {c}")

StrConstraint: TypeAlias = str | Sequence[str]
def parse_StrConstraint(c: StrConstraint) -> _Constraint:
  if isinstance(c, str):
    return _EqConstraint(c)
  else:
    return _OrConstraint(map(_EqConstraint, c))
