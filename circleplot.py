from math import sqrt

import functools
import itertools

import matplotlib.pyplot as plt
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