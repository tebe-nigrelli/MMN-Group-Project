from math import sqrt
from numbers import Real

import functools
import itertools
import matplotlib

import matplotlib.pyplot as plt
from matplotlib.figure import Figure, SubFigure
from matplotlib.axes import Axes
import seaborn as sns

import numpy as np

from constraints import *
from dataset import *

df_spike = get_spike_info(use_rates=True,
                          stimulus_name=EQ('drifting_gratings'),
                          isi_violations=RANGE(None, 0.7),
                          orientation=NOT(EQ('null')))

df_groupby = df_spike.reset_index().groupby('structure_acronym')
n = len(df_groupby)
sup_fig = plt.figure()
sup_fig.suptitle('Drifting Grating Unit Orientation Spike Rates')
figs = sup_fig.subfigures(int(sqrt(n)), int(sqrt(n)), squeeze=False)
for fig, (region, df) in zip(figs.flatten(), df_groupby):
  n = len(df['unit_id'].unique())
  axs = fig.subplots(int(sqrt(n)), int(sqrt(n)), squeeze=False,
                     subplot_kw={"projection": "polar"},
                     sharey=True)
  fig.suptitle(region)
  for ax, (unit_id, df) in zip(axs.flatten(), df.groupby('unit_id')):
    ax.set_title('')
    ax.set_xticks([0.0], labels=[''])
    ax.set_yticks([])
    df_data = df.groupby('orientation')[['spike_mean']].mean().reset_index()
    df_data['orientation'] *= np.pi / 180
    ax.bar('orientation', 'spike_mean', width = np.pi * 45 / 180, data=df_data)
sup_fig.savefig(f'orientation_spike_rates.svg')

@overload
def plot_polar_orientation_spike_rates(
    fig: None, *,
    subfigures_kw: dict[str, Any] = {},
    subplots_kw: dict[str, Any] = {'subplot_kw': {'projection': 'polar'}, 'sharey': True},
    **kwargs
) -> tuple[Figure, dict[str, SubFigure], dict[tuple[str, int], Axes]]:
  ...
@overload
def plot_polar_orientation_spike_rates(
    fig: Figure, *,
    subfigures_kw: dict[str, Any] = {},
    subplots_kw: dict[str, Any] = {'subplot_kw': {'projection': 'polar'}, 'sharey': True},
    **kwargs
) -> tuple[Figure, dict[str, SubFigure], dict[tuple[str, int], Axes]]:
  ...
@overload
def plot_polar_orientation_spike_rates(
    fig: SubFigure, *,
    subfigures_kw: dict[str, Any] = {},
    subplots_kw: dict[str, Any] = {'subplot_kw': {'projection': 'polar'}, 'sharey': True},
    **kwargs
) -> tuple[SubFigure, dict[str, SubFigure], dict[tuple[str, int], Axes]]:
  ...
def plot_polar_orientation_spike_rates(
    fig: Optional[Figure|SubFigure] = None, *, 
    subfigures_kw: dict[str, Any] = {},
    subplots_kw: dict[str, Any] = {'subplot_kw': {'projection': 'polar'}, 'sharey': True},
    **kwargs
) -> tuple[Figure|SubFigure, dict[str, SubFigure], dict[tuple[str, int], Axes]]:

  def min_difference(seq: Sequence[Real]) -> Real:
    "Return the minimum absolute difference between different items in `seq`."
    return min(min(abs(i1 - i2) for i2 in seq if i2 is not i1) for i1 in seq)

  add_field_constraint('orientation', NOT(EQ('null')), kwargs)

  df = get_spike_info(use_rates=True, **kwargs) \
    .reset_index() \
    .groupby('structure_acronym')

  n = int(sqrt(len(df_groupby)))

  orientation_delta = min_difference(df_spike['orientation'].unique())

  if fig is None:
    fig = plt.figure()
  figs = fig.subfigures(n, n, squeeze=False, **subfigures_kw).flatten()
  region_subfigs = {}
  region_unit_axs = {}
  for subfig, (region, df) in zip(figs, df):
    region_subfigs[region] = subfig
    n = int(sqrt(len(df['unit_id'].unique())))
    axs = subfig.subplots(n, n, squeeze=False, **subplots_kw).flatten()
    for ax, (unit_id, df) in zip(axs, df.groupby('unit_id')):
      region_unit_axs[(region, unit_id)] = ax
      df_data = df.groupby('orientation')[['spike_mean']].mean().reset_index()
      df_data['orientation'] *= np.pi / 180
      ax.bar('orientation', 'spike_mean', width = np.pi * orientation_delta / 180, data=df_data)
  return fig, region_subfigs, region_unit_axs

for stimulus_name in ['static_gratings', 'drifting_gratings']:
  fig = plt.figure()
  _, region_subfigs, region_unit_axs = plot_polar_orientation_spike_rates(
    fig=fig.subfigures(2, 1, height_ratios=[0.05, 0.95])[1],
    stimulus_name=EQ(stimulus_name), isi_violations=RANGE(None, 0.7))
  fig.suptitle(f'{stimulus_name} orientation spike rates')
  for region, subfig in region_subfigs.items():
    subfig.suptitle(region)
  for (region, unit_id), ax in region_unit_axs.items():
    ax.set_title('')
    ax.set_xticks([0.0], labels=[''])
    ax.set_yticks([])
  fig.savefig(IMAGE_DIR / f'{stimulus_name}_orientation_spike_rates.svg')
  
