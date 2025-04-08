from typing import *
import pathlib
from constraints import *
import warnings

DEBUG: Final[bool] = False
EXAMPLE: Final[bool] = False

def example(x):
  if EXAMPLE:
    return x

DATA_DIR: Final[pathlib.Path] = pathlib.Path('./data/')
"""Path to the data directory, relative to project root."""
DATA_DIR.mkdir(parents=True, exist_ok=True)

MANIFEST_PATH: Final[pathlib.Path] = DATA_DIR / 'manifest.json'
"""Path to the manifest file, relative to project root."""

from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
from allensdk.brain_observatory.ecephys.ecephys_session import EcephysSession
Cache: TypeAlias = EcephysProjectCache
Session: TypeAlias = EcephysSession

CACHE_TIMEOUT: Final[int] = 30*60 # 30 minutes

CACHE: Final[Cache] = EcephysProjectCache.from_warehouse(manifest=MANIFEST_PATH, timeout=CACHE_TIMEOUT)
"""The primary cache object."""

SESSIONS_TABLE = CACHE.get_session_table()
"""Dataframe of available sessions."""

SESSION_IDS: Final[Sequence[int]] = SESSIONS_TABLE.index
"""List of available session ids."""

CURRENT_SESSION_ID: Final[int] = 715093703
"""ID of the primary session to work on."""
assert CURRENT_SESSION_ID in SESSION_IDS

CURRENT_SESSION: Final[Session] = CACHE.get_session_data(CURRENT_SESSION_ID)
"""The primary session object to work on."""
with warnings.catch_warnings():
  if DEBUG: print("Loading metadata...")
  CURRENT_SESSION.metadata
  if DEBUG: print("Loading metadata... Done")

def get_sessions(**kwargs):
  """Return a table of the matching sessions.

  The following filters are meaningful:
  - published_at                (time)
  - specimen_id                 (integer, key)
  - session_type                ('brain_observatory_1.1' or 'functional_connectivity')
  - age_in_days                 (float)
  - sex                         ('M' or 'F')
  - full_genotype               (string)
  - unit_count                  (integer)
  - channel_count               (integer)
  - probe_count                 (integer)
  - ecephys_structure_acronyms  (list of strings)

  If an argument `__total__=False` is passed, additional filters may
  be provided with no effect on the result.

  """
  return filter_df(SESSIONS_TABLE, FIELD(**kwargs))

def get_session_ids(**kwargs):
  """Return the matching session ids.

  See `get_sessions` for the list of meaningful filters.

  """
  return get_sessions(**kwargs).index

def get_units(ecephys_structure_acronym = None,
              unit_ids = None,
              session: Session = CURRENT_SESSION,
              **kwargs):
  """Return a `Session.units` dataframe of the matching units in `session`.

  The `unit_ids` argument narrows the stimulus presentations
  considered to those whose id it contains.

  The following filters are meaningful:
  - waveform_PT_ratio                      (float)
  - waveform_amplitude                     (float)
  - amplitude_cutoff                       (float)
  - cluster_id                             (integer, key)
  - cumulative_drift                       (float)
  - d_prime                                (float or null)
  - firing_rate                            (float)
  - isi_violations                         (float)
  - isolation_distance                     (float or null)
  - L_ratio                                (float or null)
  - local_index                            (integer)
  - max_drift                              (float)
  - nn_hit_rate                            (float or null)
  - nn_miss_rate                           (float or null)
  - peak_channel_id                        (integer, key)
  - presence_ratio                         (float)
  - waveform_recovery_slope                (float or null)
  - waveform_repolarization_slope          (float)
  - silhouette_score                       (float or null)
  - snr                                    (float)
  - waveform_spread                        (float)
  - waveform_velocity_above                (float or null)
  - waveform_velocity_below                (float or null)
  - waveform_duration                      (float)
  - filtering                              (string)
  - probe_channel_number                   (integer)
  - probe_horizontal_position              (integer)
  - probe_id                               (integer)
  - probe_vertical_position                (integer)
  - structure_acronym                      (string)
  - ecephys_structure_id                   (float, key)
  - ecephys_structure_acronym              (string)
  - anterior_posterior_ccf_coordinate      (float or null)
  - dorsal_ventral_ccf_coordinate          (float or null)
  - left_right_ccf_coordinate              (float or null)
  - probe_description                      (string, probeA..F)
  - location                               (object)
  - probe_sampling_rate                    (float)
  - probe_lfp_sampling_rate                (float)
  - probe_has_lfp_data                     (bool)

  If an argument `__total__=False` is passed, additional filters may
  be provided with no effect on the result.

  """
  if ecephys_structure_acronym is not None:
    kwargs['ecephys_structure_acronym'] = ecephys_structure_acronym

  units = session.units
  if unit_ids is not None:
    units = units.loc[unit_ids]

  return filter_df(units, FIELD(**kwargs))

def get_unit_ids(*args, **kwargs):
  """Return the matching unit ids in `session`.

  See `get_units` for the list of meaningful filters.

  """
  return get_units(*args, **kwargs).index

def get_stimulus_presentations(stimulus_name = None,
                               stimulus_presentation_ids = None,
                               stimulus_condition_id = None,
                               session: Session = CURRENT_SESSION,
                               **kwargs):
  """Return the Sessions.stimulus_presentations dataframe of `session`.

  The `stimulus_presentation_ids` argument narrows the stimulus
  presentations considered to those whose id it contains.

  The following filters are meaningful:
  - stimulus_block           (float or null, key)
  - start_time               (float)
  - stop_time                (float)
  - contrast                 (float or null)
  - spatial_frequency        (float, string, or null)
  - frame                    (float or null)
  - stimulus_name            (string)
  - x_position               (float or null)
  - y_position               (float or null)
  - orientation              (float or null)
  - temporal_frequency       (float or null)
  - size                     (object)
  - color                    (-1.0, 1.0, or null)
  - phase                    (object)
  - duration                 (float)
  - stimulus_condition_id    (integer, key)

  If an argument `__total__=False` is passed, additional filters may
  be provided with no effect on the result.

  """
  if stimulus_name is not None:
    kwargs['stimulus_name'] = stimulus_name
  if stimulus_condition_id is not None:
    kwargs['stimulus_condition_id'] = stimulus_condition_id

  stimulus_presentations = session.stimulus_presentations
  if stimulus_presentation_ids is not None:
    stimulus_presentations = stimulus_presentations.loc[stimulus_presentation_ids]
  return filter_df(stimulus_presentations, FIELD(**kwargs))

def get_stimulus_presentation_ids(*args, **kwargs):
  """Return the matching stimulus presentation ids in `session`.

  See `get_stimulus_presentations` for a list of meaningful filters.

  """
  return get_stimulus_presentations(*args, **kwargs).index

def get_presentationwise_spike_times(session: Session = CURRENT_SESSION, **kwargs):
  """Return a table of the spike times of the matching units and stimuli.

  All filters which `get_units` and `get_stimulus_presentations`
  accept are meaningful.

  """
  kwargs['__total__'] = False
  return session.presentationwise_spike_times(
    stimulus_presentation_ids = get_stimulus_presentation_ids(session = session, **kwargs),
    unit_ids = get_unit_ids(session = session, **kwargs)
  )

def get_conditionwise_spike_statistics(use_rates: Optional[bool] = False,
                                       session: Session = CURRENT_SESSION,
                                       **kwargs):
  """Return a table of the spike statistics for each stiulus condition.

  If `use_rates` is True, use firing rates, otherwise use spike counts.

  All filters which `get_units` and `get_stimulus_presentations`
  accept are meaningful.

  """
  kwargs['__total__'] = False
  return session.conditionwise_spike_statistics(
    stimulus_presentation_ids = get_stimulus_presentation_ids(session = session, **kwargs),
    unit_ids = get_unit_ids(session = session, **kwargs),
    use_rates = use_rates
  )

def get_spike_times_with_units(session: Session = CURRENT_SESSION, **kwargs):
  """Return a table of spike times alongside the unit and stimulus information.

  All filters which `get_units` and `get_stimulus_presentations`
  accept are meaningful.

  """
  kwargs['session'] = session
  kwargs['__total__'] = False
  return get_presentationwise_spike_times(**kwargs) \
    .merge(get_stimulus_presentations(**kwargs), left_on='stimulus_presentation_id', right_index=True) \
    .merge(get_units(**kwargs), left_on='unit_id', right_index=True)

def dataset(session: Session = CURRENT_SESSION):
  ...
