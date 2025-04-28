# Question

Investigating neuron responses to stimulus orientation in static and drifting gratings

# Abstract

In this study, we analyze ecephys data from the Allen Brain Observatory to investigate how neural units in the mouse visual cortex respond to drifting gratings stimuli. Our aim is to identify brain regions and specific neurons that have a significant role in encoding stimulus orientation. We focus on the visual cortex, while keeping non-visual regions as a control group. We group neural firing rate across multiple trials and conditions to simplify the search. By selecting the most informative neurons based on their response, we construct a decoder capable of predicting stimulus orientation from neural activity.

# Introduction
Understanding how the brain encodes visual information, particularly the perception of orientation in the visual cortex, is a central goal in neuroscience. Orientation selectivity—the tendency of neurons to respond preferentially to visual stimuli of a particular orientation—is a fundamental feature of early visual processing. However, understanding the dynamics of neuron excitation in the brain is challenging due to the intrinsic complexity of inter-neuron connectivity. This investigation uses neuron firing rate statistics to differentiate cross-region and cross-stimuli behavior, shedding light on the distinction between different static grating orientations. We also uncover the relationship between neurons in different cortical regions and propose a simple model to understand 'superstar' neurons and regions.

We started our investigation by searching the _AllenSDK_ dataset for a session containing units from different brain regions. We finally chose study _750332458_ for its balanced distribution of units, especially those related to the visual cortex (VIS).

| region |     |
|--------+-----|
| grey   | 558 |
| VISal  |  71 |
| VISp   |  63 |
| VISam  |  60 |
| VISrl  |  44 |
| VISl   |  38 |
| VISpm  |  19 |
| CA1    |  16 |
| CA3    |  15 |
| DG     |   7 |
| IGL    |   5 |
| LGd    |   4 |
| IntG   |   2 |

As is clearly apparent, although most of the units are labelled 'grey', a good portion of them belongs to the Visual cortex and some recordings are present from other regions. 

# Data Processing

The dataset consists of time-aligned responses of units (neurons) to stimuli. Although both stimuli and responses are characterized by multiple features, for the purpose of our investigation we focus our observations by grouping the responses only by stimulus orientation, and focusing our statistical study on the mean firing rate of each unit, for fixed stimulus orientation.

# Exploratory Data Analysis

Our investigation focuses on the relation between unit activations and the orientation of different grating stimuli. 

**Raster Plots**
- how individual neurons response across different orientations of static gratings
- compare timing / pattern of spikes to identify any distinct temporal patterns among neurons

## Decoding static vs drifting (02_hypothesis testing // probably not included in 2 page report)

Before diving into decoding orientation we wanted to see how spike count and variability (across presentations) differed between static and drifting gratings in the visual cortex (VISam). We discovered that the spike count per presentation (spike mean) was generally much higher for the same units in drifting gratings than in static gratings. We tested these findings with a paired Wilcoxon signed-rank test (alpha=0.05) which revealed a signifcant p-value (0.000) allowing us to reject the null hypothesis that units fire equally frequently for static and drifting gratings. We then performed the same analysis on spike Coefficient of Variation (CV = std/mean) which revealed the reverse, units had greater variability when presented with static gratings (p-value 0.000). 
    We then built a two Random Forest classifier with 5-fold cross validation using just spike_mean and spike_CV 
respectively. Model 1 using spike_mean attained an accuracy of 1.000 +- 0.000 and model 2 using spike_CV attained 0.933 ± 0.033. Clearly it is easy to effectively decode whether the stimulus is static or drifting gratings from the simple measures such as spike count per presentation.
    

## Firing Rate Baseline

We first observe how spiking rate varies between regions: in general, we notice a linear relation between the log of the mean and the log of the standard deviation of the firing rates. Visually, it is clear that simply observing mean and standard deviation is not enough to characterize the brain region, though some qualitative differences can be identified. 

![](report_images/unit_firing_rate_statistics.png)

For convenience, we also include both the single plots, showing each region singularly. It should be noted that since some regions contain little data, any conclusion is heavily subject to noise, thus should be considered unreliable.

![](report_images/unit_firing_rate_statistics_single.png)

# Selection of Neurons
## Orientation Selectivity Analysis
We quantified orientation selectivity of neurons in the  visual cortex using the Orientation Selectivity Index (OSI), defined as:
$OSI = (R_{preferred} - R_{orthogonal})/(R_{preferred} + R_{orthogonal})$
where R_preferred represents the mean firing rate at the preferred orientation and R_orthogonal represents the mean firing rate at the orthogonal orientation (90° offset from preferred). This analysis revealed a subset of neurons with pronounced orientation tuning (OSI > 0.5), which will provide good grounds for training a model.

## Statistical Validation of Orientation Tuning
To statistically validate orientation tuning, we employed one-way ANOVA tests for each unit, comparing spike counts across different orientation presentations. The null hypothesis posited equal mean spike counts across all orientations, with the alternative hypothesis suggesting significant response differences to at least one orientation. This analysis identified a substantial population of neurons (p < 0.05) exhibiting statistically significant orientation tuning, confirming the presence of orientation-encoding properties within the dataset.

## Selection Criteria for Orientation-Selective Neurons
We established the following criteria for neuron selection:
1. High orientation selectivity (OSI > 0.5)
2. Statistically significant orientation tuning (ANOVA p < 0.05)

This approach yielded a population of 43  orientation-selective neurons distributed in the visual cortex, with notable concentrations in the VISal and VISl areas. The anatomical distribution of these neurons aligns with established literature on the hierarchical organization of orientation processing in the mouse brain. INCLUDE SOURCE!!!

Visualization of orientation tuning curves from representative neurons revealed diverse response profiles, including:
- Narrowly tuned neurons with a strong response to one specific orientation
- Neurons with a broader reaction to a few concurrent orientations

These different tuning properties are likely beneficial to the encoding of orientation in the visual cortex, helping to discriminate between different orientations of visual stimuli.

# Decoding Orientation from Neural Activity

## Classification Approach
To assess whether the activity patterns of orientation-selective neurons could reliably predict stimulus orientation, we implemented a machine learning approach using the spike counts of selected neurons as features. The dataset consisted of spike count responses to static grating stimuli presented at six distinct orientations (0°, 30°, 60°, 90°, 120°, and 150°). The classification task involved predicting the stimulus orientation from the corresponding neural activity patterns.

## Data Preparation and Model Training
We constructed a feature matrix where each row represented a stimulus presentation (indexed by stimulus_condition_id) and each column represented the spike count of an orientation-selective neuron. The target variable consisted of the corresponding orientation values. The dataset was stratified and split into training (70%) and testing (30%) sets to ensure proportional representation of all orientation classes.
Prior to model training, features were standardized using z-score normalization to account for differences in baseline firing rates across neurons. We evaluated three classification algorithms:

- Random Forest Classifier
- Support Vector Machine (SVM) with linear kernel
- Multinomial Logistic Regression

## Classification Performance


## Feature Importance Analysis


Performance on Drifting Gratings

**Cross Condition Analysis**
- compare neurons that show up in both static/drifting

**Temporal Dynamics**
- Analyze the time aspects of responses in drifting, compare to static

# Limitations



# Conclusion 

*Orientation Decoder*

Robust decoder that can predict the orientation of a static grating based on the neural firing patterns.

Benchmark and validate it, comparing its performance across different conditions to assess consistency and generality of neural code for orientation.

# Citations