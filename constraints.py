from abc import abstractmethod
import functools as f
import operator as op
from typing import Any, Generic, Iterable, Sequence, TypeAlias, TypeVar, overload
import typing
import pandas as pd

class _Constraint():
  """Base class for constraints.

  Defines two methods:
    `x in c` :: Returns `True` if `x` satisfies constraint `c`.
    `c.mask(df)` :: Returns a boolean `pd.Series` of the same length
                    as the index of `df`, where `True` entries are
                    rows satisfying constraint `c`.
  """
  @abstractmethod
  def __contains__(self, obj) -> bool:
    pass

  @abstractmethod
  def mask(self, df: pd.DataFrame|pd.Series) -> pd.Series:
    pass

class _ContainerConstraint(_Constraint):
  """Convenience class to define `_AndConstraint` and `_OrConstraint`,
  which both take either an iterable of constraints or some amount of
  constraints.

  """
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
  """Match object if constraint `c` does not match."""
  def __init__(self, c: _Constraint):
    self.c = c

  def __contains__(self, obj):
    return obj in self.c

  def mask(self, df):
    return ~self.c.mask(df)
    
class _OrConstraint(_ContainerConstraint):
  """Match object if any constraint `cs` matches."""
  def __init__(self, *cs):
    super().__init__(*cs)

  def __contains__(self, obj):
    return any(obj in c for c in self.cs)

  def mask(self, df):
    return f.reduce(op.or_, (c.mask(df) for c in self.cs), pd.Series([False]*df.shape[0], index=df.index))
  
class _AndConstraint(_ContainerConstraint):
  """Match object if all constraints `cs` matches."""
  def __init__(self, *cs):
    super().__init__(*cs)

  def __contains__(self, obj):
    return all(obj in c for c in self.cs)

  def mask(self, df):
    return f.reduce(op.and_, (c.mask(df) for c in self.cs), pd.Series([True]*df.shape[0], index=df.index))
  
class _EqConstraint(_Constraint):
  """Match object if equal to `obj`."""
  def __init__(self, obj: Any):
    self.obj = obj

  def __contains__(self, obj):
    return obj == self.obj

  def mask(self, df):
    return df == self.obj
  
class _RangeConstraint(_Constraint):
  """Match object if between `lb` and `ub`.

  `lb` and `ub` are the lower and upper bounds respectively.  If
  either is `None`, then the corresponding direction is unbounded.

  `lb_strict` and `ub_strict` determine whether the corresponding
  bounds are strict (not matching the bound - a.k.a exclusive) or lax
  (matching the bound - a.k.a inclusive).

  """
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

# The classes NOT, OR, AND, and RANGE are there so we can
# unambiguously type our constraints, while maintaining
# context-dependence.
  
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
    case _:
      typing.assert_never
      raise Exception(f"Invalid numerical constraint {c}")

StrConstraint: TypeAlias = str \
  | Sequence['StrConstraint']  \
  | NOT['StrConstraint']       \
  | OR['StrConstraint']        \
  | AND['StrConstraint']
  
def parse_StrConstraint(c: StrConstraint) -> _Constraint:
  match c:
    case str():
      return _EqConstraint(c)
    case NOT(c):
      return _NotConstraint(parse_StrConstraint(c))
    case AND(cs):
      return _AndConstraint(map(parse_StrConstraint, cs))
    case OR(cs) | [*cs]:
      return _OrConstraint(map(parse_StrConstraint, cs))
    case _:
      typing.assert_never
      raise Exception(f"Invalid string constraint {c}")
