# A Data-Efficient Demand Generation Framework for Multi-Agent Last-Mile Delivery via Fuzzy Logic

Master Dissertation Project at Imperial College London.

**Program Name:** Transport with Data Science

**Supervisor:** Prof. Panagiotis Angeloudis

## Project Overview
This project demonstrates a complete workflow from synthetic population to synthetic order generation. 
It provides a reusable foundation for further logistics analysis and modeling.

![Project Framework](dissertation/Dissertation%20Figures/study_framework.png)
*Figure: Project Framework*


## Installation & Dependencies
- See details in *environment.yml* file.

## Data Description
### Input Data
- [2021 UK census data](https://www.ons.gov.uk/census)
![UK Census Data](dissertation/Dissertation%20Figures/poster-census.png)

- [Statista Reports](https://www.statista.com/markets/413/topic/457/b2c-e-commerce/#overview)
![Statista Data](dissertation/Dissertation%20Figures/poster-reports.png)

### Output Data
- Synthetic population with different instance size. 
- Synthetic orders with different instance size and random seeds. 

### Case Study Data
The proposed framework is applied in Inner London Area (ILA).
![Case Study Area: ILA](dissertation/Dissertation%20Figures/lad.png)
*Figure: Case Study Area: Inner London Area (Borough Level)*


## Code / Notebook Structure
### 1 Synthetic Population
Using census data to set constrains and using Iterative Proportional Fitting to fit the synthetic population.  

![Synthetic Population Framework](dissertation/Dissertation%20Figures/poster-IPF-flowchart.png)
*Figure: Workflow of Synthetic Population*

### 2 Synthetic Order
Using multi-sources to model the e-commerce behaviour, then generate synthetic orders with different population size and random seeds.
![Synthetic Order Generation Framework](dissertation/Dissertation%20Figures/poster-syn-order-flowchart.png)
*Figure: Workflow of Synthetic Order Generation*

### 3 Data Generation Framework Validation
To validate the effectiveness of the proposed method, we introduce a third-party source by using Jensen-Shannon Divergence (JSD) as an indicator. A smaller JSD value signifies a better fit of the synthetic order to the real distribution, demonstrating the accuracy of the synthetic model.
![Synthetic Customer Age JSD Result](dissertation/Dissertation%20Figures/jsd-age.png)
*Figure: Synthetic Customer Age JSD*

![Synthetic Order Category JSD Result](dissertation/Dissertation%20Figures/jsd-ord.png)
*Figure: Synthetic Order Category JSD*

## Results / Visualization
The notebook outputs synthetic population results and corresponding visualizations, providing an intuitive view of the outcomes.

![Synthetic Population Map](dissertation/Dissertation%20Figures/synpop-map_page-0001.jpg)

*Figure: Synthetic Population Map*

![Synthetic Order Map](dissertation/Dissertation%20Figures/synord-map_page-0001.jpg)
*Figure: Synthetic Order Map*

## Usage
1. Clone or download the project  
2. Launch Jupyter Notebook in your local environment  
3. Run the notebook cells in sequence to complete the simulation and population synthesis workflow  