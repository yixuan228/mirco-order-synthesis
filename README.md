# A Data-Efficient Demand Generation Framework for Multi-Agent Last-Mile Delivery via Fuzzy Logic

Master Dissertation Project at Imperial College London.

**Program Name:** Transport with Data Science

**Supervisor:** Prof. Panagiotis Angeloudis

## Project Overview
This project demonstrates a complete workflow from synthetic population to synthetic order generation. 
It provides a reusable foundation for further logistics analysis and modeling.

## Installation & Dependencies
- See details in *environment.yml* file.

## Data Description
- **Input Data**: 
    - [2021 UK census data](https://www.ons.gov.uk/census)
    - [Statista](https://www.statista.com/markets/413/topic/457/b2c-e-commerce/#overview)
- **Output Data**: 
    - Synthetic population with different instance size. 
    - Synthetic orders with different instance size and random seeds. 

## Code / Notebook Structure
- **1 Synthetic Population**: Using census data to set constrains and using Iterative Proportional Fitting to fit the synthetic population.  
- **2 Synthetic Order**: Using multi-sources to model the e-commerce behaviour, then generate synthetic orders with different population size and random seeds.
- **3 Data Generation Framework Validation**: Introduce third-party source to validate the effectiveness of the proposed method.

## Usage
1. Clone or download the project  
2. Launch Jupyter Notebook in your local environment  
3. Run the notebook cells in sequence to complete the simulation and population synthesis workflow  

## Results / Visualization
The notebook outputs synthetic population results and corresponding visualizations, providing an intuitive view of the outcomes.


![Synthetic Order Map](dissertation/Dissertation%20Figures/synord-map.svg)

![Synthetic Population Map](dissertation/Dissertation Figures/synpop-map_page-0001.jpg)