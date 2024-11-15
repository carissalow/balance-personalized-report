import pandas as pd 
import numpy as np
import yaml

from sqlalchemy import create_engine

def load_credentials(group):
    with open("../credentials.yaml") as file:
        credentials = yaml.safe_load(file)[group]
    return credentials

def connect_to_database(credentials):
    user = credentials["user"]
    password = credentials["password"]
    host = credentials["host"]
    name = credentials["database"]

    engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{name}")
    connection = engine.connect()
    return connection

def generate_survey_query(pId):
    return f""" 
    select 
        r.surveyId as survey_id, 
        r.pId as pid, 
        p.start_date,
        p.end_date,
        r.date, 
        r.startTime as start_time, 
        r.endTime as end_time,
        r.goodnessScore as goodness_score, 
        d.activityId as activity_id, 
        a.name as activity_name,
        d.duration as activity_score
    from survey_responses as r
    left join survey_response_details as d on r.surveyId = d.surveyId
    left join (
        select activityId, name 
        from user_activities 
        union 
        select activityId, name
        from activities
    ) as a on d.activityId = a.activityId
    left join (
        select pId, startDate as start_date, endDate as end_date
        from user_study_phases
        where phaseId = 'PHASE_1'
    ) as p on r.pId = p.pId
    where 
        r.sId = 'DAILY' and 
        r.pID = '{pId}';
    """

def clean_goodness_scores(data):
    data["goodness_score"] = data["goodness_score"].fillna(-1)
    return data

def clean_activity_scores(data):
    SWITCH_DATE = "2024-10-18" # approx date we switched from activity duration to activity rating
    data["activity_score"] = np.where(data["date"] <= pd.to_datetime(SWITCH_DATE).date(), -1, data["activity_score"])
    return data

def clean_activity_names(data):
    replacements = {
        "Use social Media": "Use social media",
        "Go to Therapy": "Go to therapy"
    }
    for key, value in replacements.items():
        data["activity_name"] = data["activity_name"].str.replace(key, value)
    data["activity_name"] = data["activity_name"].str.strip().apply(lambda s: s[:1].upper() + s[1:])
    return data

def clean_dates(data):
    data["date"] = pd.to_datetime(data["date"])
    data["day_of_week"] = data["date"].dt.dayofweek
    data["day_name"] = data["date"].dt.day_name()
    return data

def clean_survey_data(data):
    return (
        data
        .pipe(clean_goodness_scores)
        .pipe(clean_activity_scores)
        .pipe(clean_activity_names)
        .pipe(clean_dates)
    )

def pull_daily_survey_data(pid):
    GROUP = "balance-test"

    credentials = load_credentials(GROUP)
    con = connect_to_database(credentials)

    survey_query = generate_survey_query(pid)
    survey_data = pd.read_sql(survey_query, con)
    survey_data_clean = clean_survey_data(survey_data)

    con.close()
    return survey_data_clean

def generate_fitbit_query(pid):
    return f""" 
    select
        pId as pid, 
        date, 
        fitbitDataType as fitbit_data_type, 
        value as fitbit_data_value
    from fitbit_data
    where 
        pId = '{pid}' and 
        date >= (select startDate from user_study_phases where pId = '{pid}' and phaseID = 'PHASE_1') and
	    date <= (select endDate from user_study_phases where pId = '{pid}' and phaseID = 'PHASE_1'); 
    """

def clean_fitbit_data(fitbit_data):
    fitbit_data_clean = (
        fitbit_data
        .pivot(
            index=["pid", "date"], 
            columns="fitbit_data_type", 
            values="fitbit_data_value"
        )
        .reset_index()
        .filter(["pid", "date", "heartrate", "sleep", "steps"])
        .fillna({"heartrate":0, "sleep":0, "steps":0})
        .assign(
            date = lambda x: pd.to_datetime(x["date"]),
            has_fitbit = lambda x: np.where(x["heartrate"] == 0, 0, 1)
        )
    )
    return fitbit_data_clean

def pull_daily_fitbit_data(pid):
    GROUP = "balance-test"

    credentials = load_credentials(GROUP)
    con = connect_to_database(credentials)
    fitbit_query = generate_fitbit_query(pid)
    fitbit_data = pd.read_sql(fitbit_query, con)
    if not fitbit_data.empty:
        fitbit_data_clean = clean_fitbit_data(fitbit_data)
    else:
        fitbit_data_clean = pd.DataFrame(columns=["pid", "date", "heartrate", "sleep", "steps"])

    con.close()
    return fitbit_data_clean