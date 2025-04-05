from typing import Any, Callable, Final, Optional, Sequence, TypeAlias
from pathlib import Path

import pandas as pd

from constraints import (
  NOT, OR, AND, RANGE,
  NumConstraint, parse_NumConstraint,
  StrConstraint, parse_StrConstraint,
)

RUN_EXAMPLES: Final[bool] = False

DATA_DIR: Final[Path] = Path('./data/')
"""Path to the data directory, relative to project root."""
DATA_DIR.mkdir(parents=True, exist_ok=True)

MANIFEST_PATH: Final[Path] = DATA_DIR / 'manifest.json'
"""Path to the manifest file, relative to project root."""

from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
from allensdk.brain_observatory.ecephys.ecephys_session import EcephysSession
Cache: TypeAlias = EcephysProjectCache
Session: TypeAlias = EcephysSession

CACHE: Final[Cache] = EcephysProjectCache.from_warehouse(manifest=MANIFEST_PATH, timeout=30*60)
"""The primary cache object."""

SESSIONS_TABLE = CACHE.get_session_table()
"""Dataframe of available sessions."""

SESSION_IDS: Final[Sequence[int]] = list(SESSIONS_TABLE.index)
"""List of available session ids."""

CURRENT_SESSION_ID: int = 715093703
"""ID of the primary session to work on."""
assert CURRENT_SESSION_ID in SESSION_IDS

CURRENT_SESSION: Session = CACHE.get_session_data(CURRENT_SESSION_ID)
"""The primary session object to work on."""

def _reduce_constraints(df: pd.DataFrame, *cs: tuple[str, Any, Callable]):
  for colname, constraint, parser in cs:
    if constraint is not None:
      df = df[parser(constraint).mask(df[colname])]
  return df

def units(ecephys_structure_acronym: Optional[StrConstraint] = None,
          isi_violations:            Optional[NumConstraint] = None,
          snr:                       Optional[NumConstraint] = None,
          probe_id:                  Optional[NumConstraint] = None,
          session: Session = CURRENT_SESSION):
  """Return the `Session.units` dataframe of `session`.

  The dataframe can be filtered by the following fields:

    `ecephys_structure_acronym` (String)
    `isi_violations`            (Numeric)
    `snr`                       (Numeric)
    `probe_id`                  (Numeric)

  See the comment at the top of constraints.py for the format of
  constraints.

  """
  return _reduce_constraints(
    session.units,
    ('ecephys_structure_acronym' , ecephys_structure_acronym , parse_StrConstraint),
    ('isi_violations'            , isi_violations            , parse_NumConstraint),
    ('snr'                       , snr                       , parse_NumConstraint),
    ('probe_id'                  , probe_id                  , parse_NumConstraint)
  )

def unit_ids(**kwargs):
  return units(**kwargs).index

def stimulus_presentations(stimulus_name:         Optional[StrConstraint] = None,
                           duration:              Optional[NumConstraint] = None,
                           stimulus_condition_id: Optional[NumConstraint] = None,
                           temporal_frequency:    Optional[NumConstraint] = None,
                           spatial_frequency:     Optional[NumConstraint] = None,
                           orientation:           Optional[NumConstraint] = None,
                           contrast:              Optional[NumConstraint] = None,
                           x_position:            Optional[NumConstraint] = None,
                           y_position:            Optional[NumConstraint] = None,
                           color:                 Optional[NumConstraint] = None,
                           phase:                 Optional[NumConstraint] = None,
                           session: Session = CURRENT_SESSION):
  return _reduce_constraints(
    session.stimulus_presentations,
    ('stimulus_name'         , stimulus_name         , parse_StrConstraint),
    ('duration'              , duration              , parse_NumConstraint),
    ('stimulus_condition_id' , stimulus_condition_id , parse_NumConstraint),
    ('temporal_frequency'    , temporal_frequency    , parse_NumConstraint),
    ('spatial_frequency'     , spatial_frequency     , parse_NumConstraint),
    ('orientation'           , orientation           , parse_NumConstraint),
    ('contrast'              , contrast              , parse_NumConstraint),
    ('x_position'            , x_position            , parse_NumConstraint),
    ('y_position'            , y_position            , parse_NumConstraint),
    ('color'                 , color                 , parse_NumConstraint),
    ('phase'                 , phase                 , parse_NumConstraint),
  )

def stimulus_presentation_ids(**kwargs):
  return stimulus_presentations(**kwargs).index

def dataset(session: Session = CURRENT_SESSION):
  ...
