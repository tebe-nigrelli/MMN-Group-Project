from math import sqrt

import functools
import itertools

import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np

from constraints import *
from dataset import *

df_spike = get_spike_info(use_rates=True,
                          stimulus_name=EQ('static_gratings'), # ISIN(['static_gratings', 'drifting_gratings']),
                          isi_violations=RANGE(None, 0.7))

for region, df in df_spike.reset_index().groupby('structure_acronym'):
  n = len(df['unit_id'].unique())
  fig, axs = plt.subplots(int(sqrt(n)), int(sqrt(n)), squeeze=False,
                          subplot_kw={"projection": "polar"},
                          sharey=True)
  fig.suptitle(region)
  for ax, (unit_id, df) in zip(axs.flatten(), df.groupby('unit_id')):
    ax.set_title(str(unit_id), size='small', y=0.95)
    ax.set_xticks([0.0])
    df_data = filter_df(df.groupby('orientation')[['spike_mean']].mean().reset_index(),
                        FIELD(orientation=NOT(EQ('null'))))
    df_data['orientation'] *= np.pi / 180
    ax.bar('orientation', 'spike_mean', width = np.pi * 15 / 180, data=df_data)
  fig.savefig(f'orientation_spike_rates_{region}.svg')
  break

