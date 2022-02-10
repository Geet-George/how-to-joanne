# Workplan for AC3-dropsondes

**This is a working repository: Many features/bug fixes/updates to come...**
I wouldn't trust this README to be constantly updated till there is a stable version release.

# Planned Workflow
-----------------
### 1. Raw data from flight

:arrow_down: 

### 2. Processing from [ASPEN](https://www.eol.ucar.edu/software/aspen)

:arrow_down: 

### 3. Config file ([sample file here](https://github.com/Geet-George/how-to-joanne/blob/main/run_config.cfg))

    - Flight details
    - Timestamps for circle start and end (if applicable) / optionally, flight segments
    - Level of processing
    - Quicklooks (optional)

:arrow_down: 

### 4. Run package

####  Data processing

    - Quality control 
    - Interpolating to uniform, vertical grid
    - Area-averaged circle products
#### Quicklooks


    - Map of dropsonde launch locations
        - ice-ocean-land masks
        - column moisture (as marker of colour) / any other variable of interest?
    - Slices of dropsonde profiles
    - Mean profile with variability 
        - Measured variables
            - Temperature
            - Pressure
            - Humidity
            - Horizontal winds
        - Derived variables
            - Static energy (moist, dry and sat. moist)
            - Divergence
            - Vorticity
            - Vertical velocity
    - Drift profiles
    
#### Final dataset

    - Full data processing
    - Levels 0 to 4 (similar to EUREC4A? Any other suggestions?)

--------------
<!-- $^1$ circle could also be any other pattern decided for the flight (e.g. alternatives such as a mattress pattern can be flown)
$^2$ flight segmentation YAML flights include segment kinds from which circles are identified -->

# how-to-joanne

## What is this repo for?
Tutorial on working with JOANNE and potential repo to carry forward the functions for a generic JOANNE++ package

## This repo contains (or is planned to contain): 

(a) notebooks that will work with JOANNE data in a tutorial format to familiarise users with the dataset
(b) notebooks that can be extended to work beyond the JOANNE dataset, for similar data from other campaigns

:warning::heavy_exclamation_mark: Requires cloning the [JOANNE repo](https://github.com/Geet-George/JOANNE) and installing it in working environment if additional quality control and gridding (as per JOANNE L3) or circle products (as per JOANNE L4) are to be used :heavy_exclamation_mark::warning:

Think of this repo as a sandbox for JOANNE++

## Idea behind JOANNE++ 

A package that can be used for dropsonde processing from different field campaigns that will include:

(a) scripts to process raw data and create CF-conforming datasets
(b) scripts to create quicklooks during field operations
(c) an intake-catalog that can help access dropsonde data from across campaigns via a single access point

