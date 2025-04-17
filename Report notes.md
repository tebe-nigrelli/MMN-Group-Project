# Question

How is orientation perceived in the neural response of mice?

# Abstract

In this study, we analyze ecephys data from the Allen Brain Observatory to investigate how neural units in the mouse visual cortex respond to drifting gratings stimuli. Our aim is to identify brain regions and specific neurons that have a significant role in encoding stimulus orientation. Focusing on the __ REGIONS, we evaluate neural firing rate across multiple trials and conditions. By selecting the most informative neurons based on their response, we construct a decoder capable of predicting stimulus orientation from neural activty. COMMENT ON PERFORMANCE
Understanding the dynamics of neuron excitation in the brain is a difficult task due to the intrinsic complexity of inter-neuron connectivity. This investigation uses neuron firing rate statistics to differentiate cross-region and cross-stimuli behavior and shed light on the distinction between different static grating orientations. We uncover the relation between neurons in different cortical regions and propose a simple model to understand 'superstar' neurons and regions.

# Introduction
Understanding how the brain encodes visual information is a central goal in neuroscience. In particular, the perception of orientation in the visual cortex has been extensively studied as a model for sensory coding. Orientation selectivity—the tendency of neurons to respond preferentially to visual stimuli of a particular orientation—is a fundamental feature of early visual processing.

## Data Visualization

**Raster Plots**
- how individual neurons response across different orientations of static gratings
- compare timing / pattern of spikes to identify any distinct temporal patterns among neurons

## Single-Neuron Analysis

**Firing Rate Calculation**
- for each neuron, average firing rate across all presented orientations
- orientation "tuning curves"? to determine each neuron's preferred orientation

**Selection Criteria**
- identify neurons that exhibit strong, consistent responses
- use statistical measures to pick neurons for reliable orientation encoding: OSI?

## Population-Level Analysis

**Grouping and Comparison**
- aggregate responses from groups or regions of neurons to explore population-level encoding of orientation
- compare activity patterns across brain regions 

**Cross Neuron Correlations**
- correlation of responses among neurons to detect collective dynamics or "network-level" integration of orientation info

# Classifier

**Classifier Construction**
- based on indiv neurons (or groups) that show clear tuning, build a classification model to predict orientation of static

**Training and Validation**
- accuracy / precision / recall you know the drill

## Comparative Analysis: Static vs Drifting Gratings

**Cross Condition Analysis**
- compare neurons that show up in both static/drifting

**Temporal Dynamics**
- analyse the time aspects of responses in drifting, compare to static


## Final Product

*Orientation Decoder*

Robust decoder that can predict the orientation of a static grating based on the neural firing patterns.

Benchmark and validate it, comparing its performance across different conditions to assess consistency and generality of neural code for orientation.

# Methods
Present the findings of the study, including statistical analyses, figures, and tables where applicable.

Interpret the results, discuss their significance, compare them with previous research, and highlight potential limitations and future directions.

Summarize the key findings and their implications in the field of neuroscience.
