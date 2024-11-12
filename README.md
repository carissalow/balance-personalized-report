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

1. Pulling raw data from the BALANCE MySQL database  
2. Wrangling and summarizing data for tables and plots  
3. Rendering a personalized data visualization report  

Rendered participant-specific reports can be found in `output/balance_report_[PID].html`.    