from typing import Any, Callable, Final, Optional, Sequence, TypeAlias, TypedDict
from pathlib import Path

import pandas as pd

from constraints import *

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

def sessions(**kwargs):
  """Filter `SESSIONS_TABLE`."""
  return filter_df(SESSIONS_TABLE, FIELD(**kwargs))

def session_ids(**kwargs):
  return sessions(**kwargs).index
  
def units(ecephys_structure_acronym = None,
          session: Session = CURRENT_SESSION,
          **kwargs):
  """Return the `Session.units` dataframe of `session`.

  Filter based on arguments provided."""
  if ecephys_structure_acronym is not None:
    kwargs['ecephys_structure_acronym'] = ecephys_structure_acronym
  return filter_df(session.units, FIELD(**kwargs))

def unit_ids(**kwargs):
  return units(**kwargs).index

def stimulus_presentations(stimulus_name = None,
                           stimulus_condition_id = None,
                           session: Session = CURRENT_SESSION,
                           **kwargs):
  """Return the Sessions.stimulus_presentations dataframe of `session`.

  Filter based on arguments provided."""
  if stimulus_name is not None:
    kwargs['stimulus_name'] = stimulus_name
  if stimulus_condition_id is not None:
    kwargs['stimulus_condition_id'] = stimulus_condition_id
  return filter_df(session.stimulus_presentations, FIELD(**kwargs))

def stimulus_presentation_ids(**kwargs):
  return stimulus_presentations(**kwargs).index

def presentationwise_spike_times(session: Session = CURRENT_SESSION, **kwargs):
  if '__total__' in kwargs:
    del kwargs['__total__']
  return session.presentationwise_spike_times(
    stimulus_presentation_ids = stimulus_presentation_ids(session = session, __total__ = False, **kwargs),
    unit_ids = unit_ids(session = session, __total__ = False, **kwargs)
  )

def conditionwise_spike_statistics(use_rates: Optional[bool] = False,
                                   session: Session = CURRENT_SESSION,
                                   **kwargs):
  if '__total__' in kwargs:
    del kwargs['__total__']
  return session.conditionwise_spike_statistics(
    stimulus_presentation_ids = stimulus_presentation_ids(session = session, __total__ = False, **kwargs),
    unit_ids = unit_ids(session = session, __total__ = False, **kwargs),
    use_rates = use_rates
  )

def dataset(session: Session = CURRENT_SESSION):
  ...
