# tommaso.ipynb



## |‾‾‾‾‾‾‾‾‾‾ Filter sessions ‾‾‾‾‾‾‾‾‾‾‾‾‾|
from constraints import filter_df
from dataset import get_stimulus_presentation_ids

brain_obs_sessions = sessions[(sessions.session_type == "brain_observatory_1.1")]
uh_brain_obs_sessions = brain_obs_sessions[(brain_obs_sessions["unit_count"] >= 650)]
required_regions = {"VISp", "VISl", "VISal", "VISpm", "VISam"}
regions_uh_brain_obs_sessions = uh_brain_obs_sessions[
    uh_brain_obs_sessions["ecephys_structure_acronyms"].apply(
        lambda x: all(region in str(x) for region in required_regions))]
## |------------ Equivalent to -------------|
get_sessions(session_type='brain_observatory_1.1',
             unit_count=RANGE(650, None), 
             ecephys_structure_acronyms=AND(map(CONTAINS,{"VISp", "VISl", "VISal", "VISpm", "VISam"})))
## |---------------- or --------------------|
get_sessions(session_type='brain_observatory_1.1',
             unit_count=RANGE(650, None), 
             ecephys_structure_acronyms=AND(CONTAINS("VISp"),
                                            CONTAINS("VISl"),
                                            CONTAINS("VISal"),
                                            CONTAINS("VISpm"),
                                            CONTAINS("VISam")))
## |________________________________________|





## |‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|
mask = (table['stimulus_name'] == 'static_gratings') & (table["orientation"] == 0.0) #change orientation as well
static_gratings = table[mask] 
## |--------------- Equivalent to -----------------|
filter_df(table, FIELD(stimulus_name='static_gratings',
                       orientation=0.0))
## |_______________________________________________|




## |‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|
static_gratings_ind = static_gratings.index.values
visam_ids = session2.units[session2.units["ecephys_structure_acronym"] == "VISam"].index.values #not used yet
spike_times_static = session2.presentationwise_spike_times(
    stimulus_presentation_ids=static_gratings_ind,
    unit_ids =visam_ids
)
## |--------------- Equivalent to -----------------|
session2.presentationwise_spike_times(
  stimulus_presentation_ids = get_stimulus_presentation_ids(stimulus_name = 'static_gratings',
                                                            orientation = 0.0),
  unit_ids = get_unit_ids(ecephys_structure_acronym = 'VISam'))
## |------------------- or ------------------------|
get_presentationwise_spike_times(stimulus_name = 'static_gratings',
                                 orientation = 0.0,
                                 ecephys_structure_acronym = 'VISam',
                                 session = session2)
## |_______________________________________________|




## |‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|
number = 5
id0 = static_gratings.index.values[0]
idf = static_gratings.index.values[number-1]

mask = (spike_times_static["stimulus_presentation_id"] >= id0) & (spike_times_static["stimulus_presentation_id"] <= idf) 
spikes_first = spike_times_static[mask]
## |--------------- Equivalent to -----------------|
filter_df(spike_times_static,
          FIELD(stimulus_presentation_id = RANGE(id0, idf, ub_strict=True)))
## |------------------- or ------------------------|
get_presentationwise_spike_times(stimulus_name = 'static_gratings',
                                 orientation = 0.0,
                                 ecephys_structure_acronym = 'VISam',
                                 stimulus_presentation_id = RANGE(id0, idf, ub_strict=True)
                                 session = session2)
## |_______________________________________________|




# tebe.ipynb


## |‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|
df[(df['spatial_frequency'] == np.float64(0.08)) & (df['phase']==np.float64(0.5))]
## |--------------- Equivalent to -----------------|
filter_df(df, FIELD(spatial_frequency = np.float64(0.08),
                    phase = np.float64(0.5)))
## |_______________________________________________|



# utku.ipynb

## |‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|
def get_spike(session, stimuli, ecephys_structure_acronym):
  table = session.get_stimulus_table(stimuli)

  stimulus_presentation_ids = table.index.values
  unit_ids = session.units[session.units["ecephys_structure_acronym"] == ecephys_structure_acronym].index.values

  spike_counts = session.conditionwise_spike_statistics(
    stimulus_presentation_ids=stimulus_presentation_ids,
    unit_ids =unit_ids,
  )

  return spike_counts

static_spike_counts = get_spike(session, stimuli = "static_gratings", ecephys_structure_acronym="VISam")
drifting_spike_counts = get_spike(session, stimuli = "drifting_gratings", ecephys_structure_acronym="VISam")
## |--------------- Equivalent to -----------------|
static_spike_counts = get_conditionwise_spike_statistics(
  ecephys_structure_acronym = 'VISam',
  stimulus_name = 'static_gratings',
  session = session)
drifting_spike_counts = get_conditionwise_spike_statistics(
  ecephys_structure_acronym = 'VISam',
  stimulus_name = 'drifting_gratings',
  session = session)
## |_______________________________________________|

