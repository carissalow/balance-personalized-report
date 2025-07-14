# balance-personalized-report

Personalized data visualization and analysis reports for participants in the **Behavioral Activation-Led Activity eNgagement for Cancer Empowerment (BALANCE)** study at the Mobile Sensing + Health Institute at the University of Pittsburgh. These reports are provided at the midpoint of the study to help participants explore relationships between their daily goodness ratings, activities, and Fitbit steps and sleep data, with the goal of identifying a personalized list of meaningful activities to focus on increasing during the second stage of the intervention. 

<br>

---

## Installation

1. Install [Miniconda](https://docs.anaconda.com/free/miniconda/miniconda-install/)

2. Install [Quarto](https://quarto.org/docs/get-started/) 

3. Clone the repository:

    ```bash
    git clone https://github.com/jenniferfedor/balance-personalized-report
    ```

4. Restore the Python virtual environment:

    ```bash
    cd balance-personalized-report
    conda env create -f environment.yml -n balance
    ```

5. Create a `credentials.yaml` file with the following format, filling in the host, user, and password fields:  

    ```yaml
    balance:
        database: "balance"
        host: "[BALANCE study database EC2 instance URL]"
        user: "[BALANCE study database user name]"
        password: "[BALANCE study database user password]"
        port: 3306
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

### March 2025 
- Fix bug related to Fitbit data cleaning when there were heartrate data but no steps or sleep data present in the database  
- Set infinite percent differences (i.e., due to change from score equal to 0 to score greater than 0) to 100%  

### February 2025
- Fix phase 1 date range (end date in database is 1 day after end date in REDCap)
- Fix color scale mapping for scatter plots  
- Improve label positioning for bar plots

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