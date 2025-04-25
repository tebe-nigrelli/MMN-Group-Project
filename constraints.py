from __future__ import annotations

from abc import abstractmethod
from typing import Any, Callable, Collection, Iterable, Mapping, TypeVar
import pandas as pd

"""

This module defines the Constraint class, which is a mechanism by
which you can define constraints for values.

The following constraints work for all fields:

  EQ(obj)
    Match things equal to `obj` (`x == obj`) and nothing else.

  NOT(constraint)
    Match the current object if `constraint` does not match it.

  OR(constraints...) or [constraints...]
    Match the current object if any of `constraints` matches it.

  AND(constraints...)
    Match the current object if all of `constraints` matches it.

The following constraint works for strings:

  'name'
    Match the current object if it is equal to the string `'name'`.

The following constraints work for numeric fields:

  number
    Match the current object if it is equal to `number`.

  RANGE(lb, ub, lb_strict=False, ub_strict=True)
    Match the current object if it is a number in the range [lb, ub],
    where the bounds are strict depending on `lb_strict` and
    `ub_strict`.

    `lb` and `ub` may be `None`, which signifies a lack of bound.

The following works on dataframes:

  FIELD(field=constraint...) or {'field': constraint ...}

    Match each `field` column of the given dataframe against the
    corresponding `constraint`.

    Note: When doing `x in FIELD(...)`, `x` needs to be a row of the
    dataframe, though if you're not calling that then just don't
    bother.

    Note: Technically speaking there is no need for the object to be a
    dataframe.  We are actually just checking `x[field] in constraint`
    for each pair of `field` and `constraint`.

Examples:

  If you wanted to get all units where the `isi_violations` are
  less than 0.7, you would call
  ```
    units(isi_violations=RANGE(None,0.7))
  ```
  and if you wanted those with `isi_violations` between 0.2 and 0.4,
  you would call
  ```
    units(isi_violations=RANGE(0.2,0.4))
  ```
  or equivalently,
  ```
    units(isi_violations=AND(RANGE(NONE,0.4), RANGE(0.2, 0.6)))
  ```
  even though that would be pointless.

  If you want to return all the units where the region of the brain is
  'VISrl',
  ```
    units(ecephys_structure_acronym='VISrl')
  ```
  and if you want to also include 'APN',
  ```
    units(ecephys_structure_acronym=['VISrl', 'APN'])
  ```
  or 
  ```
    units(ecephys_structure_acronym=OR('VISrl', 'APN'))
  ```

  The functions `units` and `stimulus_presentations` are actually
  simple wrappers around `filter_df` with a `FIELD` constraint.

  The call to
  ```
    stimulus_presentations(stimulus_name = 'gabors',
                           stimulus_condition_id = 1,
                           duration = RANGE(None, 0.24))
  ```
  is fully equivalent to
  ```
    filter_df(CURRENT_SESSION.stimulus_presentations,
              FIELD(stimulus_name = 'gabors',
                    stimulus_condition_id = 1,
                    duration = RANGE(None, 0.24)))
  ```
  and also to
  ```
    filter_df(CURRENT_SESSION.stimulus_presentations,
              {'stimulus_name': 'gabors',
               'stimulus_condition_id': 1,
               'duration': RANGE(None, 0.24)})
  ```

  FIELD constraints can be combined together with OR, AND, and NOT as
  well:
  ```
    filter_df(CURRENT_SESSION.stimulus_presentations,
              OR(FIELD(stimulus_name = 'gabors',
                       stimulus_condition_id = 1),
                 FIELD(stimulus_name = 'static_gratings',
                       orientation = AND(NOT(EQ('null')),
                                         RANGE(30, 60, lb_strict=False, ub_strict=False)))))
  ```

Important note: OR, AND, and FIELD short-circuit; what this means is
that if you have a column where the value is either the string 'null'
or a number, you can first make sure that you handle the 'null' case by doing
```
  AND(NOT(EQ('null')),
      ...)
```
and then handle the number case however you want in the `...` section.

"""

class Constraint():
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

  def mask(self, df: pd.DataFrame|pd.Series) -> pd.Series:
    return df.apply(self.__contains__)

class _TRUE(Constraint):
  """Always true constraint."""
  def __init__(self): return
  def __contains__(self, obj): return True
  def mask(self, df): return pd.Series(True, index=df.index)

class _FALSE(Constraint):
  def __init__(self): return
  def __contains__(self, obj): return False
  def mask(self, df): return pd.Series(False, index=df.index)

TRUE: Final[_TRUE] = _TRUE()
FALSE: Final[_FALSE] = _FALSE()

class _ContainerConstraint(Constraint):
  """Convenience class to define `_AndConstraint` and `_OrConstraint`,
  which both take either an iterable of constraints or some amount of
  constraints.

  """
  def __init__(self, *cs):
    if (len(cs) != 0 and
        isinstance(cs[0], Iterable) and
        not isinstance(cs[0], str)):
      assert len(cs) == 1
      self.cs = cs[0]
    else:
      self.cs = cs
    self.cs: Iterable[Constraint] = map(ensure_constraint, self.cs)
  
class NOT(Constraint):
  """Match object if constraint `c` does not match."""
  def __init__(self, c: Constraint):
    self.c = ensure_constraint(c)

  def __contains__(self, obj):
    return obj in self.c

  def mask(self, df):
    return ~self.c.mask(df)
    
class OR(_ContainerConstraint):
  """Match object if any constraint `cs` matches."""
  def __init__(self, *cs):
    super().__init__(*cs)

  def __contains__(self, obj):
    return any(obj in c for c in self.cs)

  def mask(self, df):
    m = pd.Series([False] * df.shape[0], index=df.index)
    for c in self.cs:
      m_new = c.mask(df)
      m |= m_new
      df = df[~m_new]
    return m
  
class AND(_ContainerConstraint):
  """Match object if all constraints `cs` matches."""
  def __init__(self, *cs):
    super().__init__(*cs)

  def __contains__(self, obj):
    return all(obj in c for c in self.cs)

  def mask(self, df):
    m = pd.Series([True]*df.shape[0], index=df.index)
    for c in self.cs:
      m_new = c.mask(df)
      m &= m_new
      df = df[m_new]
    return m

class EQ(Constraint):
  """Match object if equal to `obj`."""
  def __init__(self, obj: Any):
    self.obj = obj

  def __contains__(self, obj):
    return obj == self.obj

  def mask(self, df):
    return df == self.obj

class SATISFIES(Constraint):
  """Match object if calling `func` on it returns True."""
  def __init__(self, func: Callable):
    self.func = func

  def __contains__(self, obj):
    return bool(self.func(obj))

class ISIN(Constraint):
  """Match object if it is in `members`."""
  def __init__(self, members: Collection):
    self.members = members

  def __contains__(self, obj):
    return obj in self.members

  def mask(self, df):
    return OR(map(EQ, self.members)).mask(df)

class MEMBER(ISIN):
  """Match object if it is in `members`.

  This is a deprecated alias to `ISIN`."""
  def __init_subclass__(cls):
    import warnings
    warnings.warn("`MEMBER`, is a deprecated alias to `ISIN`.", DeprecationWarning, 2)
    return super().__init_subclass__()

class CONTAINS(Constraint):
  """Match object if it contains an element matching the constraint."""
  def __init__(self, c):
    self.c = ensure_constraint(c)

  def __contains__(self, obj):
    return any(e in self.c for e in obj)

class RANGE(Constraint):
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

_K = TypeVar('_K')
_V1 = TypeVar('_V1')
_V2 = TypeVar('_V2')
def _map_dict(func: Callable[[_V1],_V2], m: dict[_K, _V1]) -> dict[_K, _V2]:
  return {k:func(v) for k,v in m.items()}
  
class FIELD(Constraint):
  """Match object if each of its field matches the corresponding constraint."""

  def __init__(self, **kwargs: Mapping[str,Constraint|Any]):
    self.total = kwargs.get('__total__', True)
    self.fields = _map_dict(ensure_constraint, kwargs)

  def __contains__(self, obj):
    for field, constraint in self.fields.items():
      try:
        x = obj[field]
      except:
        if self.total:
          return False
      else:
        if x not in constraint:
          return False
    return True

  def mask(self, df):
    empty_mask = pd.Series([False] * df.shape[0], index=df.index)
    m = pd.Series([True] * df.shape[0], index=df.index)
    for colname, constraint in self.fields.items():
      try:
        x = df[colname]
      except:
        if self.total:
          return empty_mask
      else:
        m_new = constraint.mask(x)
        m &= m_new
        df = df[m_new]
    return m

def ensure_constraint(x: Any) -> Constraint:
  if isinstance(x, Constraint):
    return x
  if isinstance(x, Mapping):
    return FIELD(**x)
  if isinstance(x, set):
    return MEMBER(x)
  if isinstance(x, Iterable) and not isinstance(x, str):
    return OR(x)
  return EQ(x)

def filter_df(df, constraint):
  return df[ensure_constraint(constraint).mask(df)]
