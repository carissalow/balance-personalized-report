# balance-personalized-analysis

Personalized data visualizations and analyses for participants in the **Behavioral Activation-Led Activity eNgagement for Cancer Empowerment (BALANCE)** study at the Mobile Sensing + Health Institute at the University of Pittsburgh.  

<br>

---

## Installation

1. Install [Miniconda](https://docs.anaconda.com/free/miniconda/miniconda-install/)

2. Install [Quarto](https://quarto.org/docs/get-started/) 

3. Clone the repository:

    ```bash
    git clone https://github.com/jenniferfedor/balance-personalized-analysis
    ```

4. Restore the Python virtual environment:

    ```bash
    cd balance-personalized-analysis
    conda env create -f environment.yml -n balance
    ```

<br>

---

## Execution 

Run all steps of the analysis and generate a personalized report for a given participant, `PID`:

```bash
cd src
conda activate balance
bash render_participant_report.sh PID
```

Steps of the analysis include:

1. Pulling the participant's Phase 1 daily survey and Fitbit data from the study's MySQL database  
2. Wrangling and summarizing those data for tables and plots  
3. Populating the Quarto report template with those visualizations
4. Rendering the personalized report as an HTML file 

Rendered participant-specific reports can be found in `output/balance_report_[PID].html`.    

<br>

---

## Change log 

### February 2025
- Fix phase 1 date range (end date in database is 1 day after end date in REDCap)
- Fix color scale mapping for scatter plots  

### December 2024  
- Update data pull script  
- Change "goodness" to "daily goodness"  

### November 2024 
- Replace heatmaps with tables  
- Drop activity clusters  
- Improve plot scaling  
- Add column spanner to activity by day of week table  
- Add report parameterization
- Add Fitbit data to report  
- Fix bugs caused by missing or duplicated data  
- Fix miscellaneous bugs  