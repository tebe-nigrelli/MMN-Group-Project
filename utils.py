import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import tqdm
from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache

data_dir = "./allendata"
df_file = data_dir + "/" + "df.csv"

manifest_path = os.path.join(data_dir, "manifest.json")
cache = EcephysProjectCache.from_warehouse(manifest=manifest_path)

def get_dataset(session_number:int, stimuli: list, regions:list):
    session = cache.get_session_data(session_number)

    tables = [session.get_stimulus_table(stimulus) for stimulus in stimuli]
    table = pd.concat(tables)

    partial_ids = session.units[session.units["ecephys_structure_acronym"].isin(regions)]

    spike_times_drifting = session.presentationwise_spike_times(
        stimulus_presentation_ids=table.index.values,
        unit_ids=partial_ids.index.values
    )
    
    return (
        spike_times_drifting
        .merge(table, left_on="stimulus_presentation_id", right_index=True)
        .merge(session.units, left_on="unit_id", right_index=True)
    )
           
# df = get_dataset(750332458, "static_gratings", "VISam")
# df.to_csv(df_file)
# df = pd.read_csv(df_file)