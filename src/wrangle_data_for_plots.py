import pandas as pd
import numpy as np

from itertools import product
from sklearn.cluster import AgglomerativeClustering

def flatten_columns(data):
    data.columns = ['_'.join(col).rstrip('_') for col in data.columns.values]
    return data

def create_segment_sequence(row):
    return list(np.arange(row['segment_min']*10, row['segment_max']*10) / 10)

def rescale_with_midpoint(data, midpoint=0):
    min_val = np.min(data)
    max_val = np.max(data)

    # Adjust the midpoint to fall within the range [0, 1]
    # midpoint_scaled = (midpoint - min_val) / (max_val - min_val)
    def rescale_func(x):
        if x <= midpoint & midpoint != min_val:
            return 0.5 * (x - min_val) / (midpoint - min_val)
        elif x <= midpoint & midpoint == min_val:
            return 0.5 #* (x - min_val) / (midpoint - min_val)
        else:
            return 0.5 + 0.5 * (x - midpoint) / (max_val - midpoint)
    return np.vectorize(rescale_func)(data)

def get_value_box_data(survey_data, fitbit_data):
    value_descriptions = [
        "Surveys completed", 
        "Longest survey completion streak", 
        "Average goodness rating", 
        "Total activities logged", 
        "Unique activities logged", 
        "Average activity rating",
        "Days with Fitbit data",
        "Average step count",
        "Average hours of sleep"
    ]

    if not survey_data.empty:
        longest_streak = (
            survey_data
            .filter(["survey_id", "date"])
            .drop_duplicates()
            .reset_index(drop=True)
            .assign(streak_breaks = lambda x: x["date"].diff() != pd.Timedelta("1d"))
            .assign(streak_groups = lambda x: x["streak_breaks"].cumsum())
            .groupby("streak_groups")
            .agg({"date":"count"})
            .max()
            .iloc[0]
        )

        survey_value_box_stats = pd.DataFrame({
            "n_surveys": [survey_data["survey_id"].drop_duplicates().shape[0]],
            "longest_streak_days": [longest_streak],
            "avg_goodness": [survey_data[["survey_id", "goodness_score"]].drop_duplicates()["goodness_score"].mean().round(1)],
            "n_activities": [survey_data[["survey_id", "activity_id"]].drop_duplicates().shape[0]],
            "n_distinct_activities": [survey_data[["activity_id"]].drop_duplicates().shape[0]],
            "avg_activity_score": [survey_data["activity_score"].replace(-1, np.nan).mean().round(1) if not np.isnan(survey_data["activity_score"].replace(-1, np.nan).mean()) else np.nan]
        })
    
    else:
        survey_value_box_stats = pd.DataFrame({
            "n_surveys": [0],
            "longest_streak_days": [0],
            "avg_goodness": [np.nan],
            "n_activities": [0],
            "n_distinct_activities": [0],
            "avg_activity_score": [np.nan]
        })

    if not fitbit_data.empty:
        fitbit_value_box_stats = pd.DataFrame({
            "days_with_fitbit": [fitbit_data["has_fitbit"].sum()],
            "average_steps": [fitbit_data[fitbit_data["has_fitbit"] == 1]["steps"].mean().round(0).astype(int) if not np.isnan(fitbit_data[fitbit_data["has_fitbit"] == 1]["steps"].mean()) else np.nan],
            "average_sleep": [fitbit_data[fitbit_data["has_fitbit"] == 1]["sleep"].mean().round(0).astype(int) if not np.isnan(fitbit_data[fitbit_data["has_fitbit"] == 1]["sleep"].mean()) else np.nan],
        })
    
    else:
        fitbit_value_box_stats = pd.DataFrame({
            "days_with_fitbit": [0],
            "average_steps": [np.nan],
            "average_sleep": [np.nan]
        })

    value_box_stats = pd.concat([survey_value_box_stats, fitbit_value_box_stats], axis=1)

    value_box_data = (
        value_box_stats
        .melt()
        .assign(value=lambda x: x["value"].map("{:,.1f}".format).str.replace(".0", "").str.replace("nan", "N/A"))
        .assign(description=value_descriptions)
        .assign(variable = lambda x: pd.Categorical(x["variable"], categories=x["variable"].tolist()))
        .assign(
            description_x = 0.05,
            description_y = 0.15,
            value_x = 0.05,
            value_y = 0.45,
            xmin = 0,
            xmax = 1,
            ymin = 0,
            ymax = 1
        )
    )
    return value_box_data
    
def get_goodness_data(data):
    goodness_columns = ["survey_id", "date", "day_of_week", "day_name", "goodness_score"]
    goodness_data = (
        data
        .filter(goodness_columns, axis=1)
        .drop_duplicates()
        .query("goodness_score != -1") # drop any missing scores
        .reset_index(drop=True)
    )
    return goodness_data

def get_goodness_bar_plot_data(goodness_data, score_categories):
    goodness_bar_plot_data = (
        goodness_data
        .query("goodness_score != -1")
        .groupby(["goodness_score"])
        .agg({"date":"count"})
        .reset_index(drop=False)
        .assign(goodness_score = lambda x: pd.Categorical(x["goodness_score"], categories=score_categories))
        .rename(columns={"date":"n_days"})
    )
    return goodness_bar_plot_data

def get_goodness_data_per_day(goodness_data):
    goodness_per_day = (
        goodness_data
        .query("goodness_score != -1")
        .groupby(["day_of_week", "day_name"])
        .agg({"goodness_score": ["count", "mean", "min", "max"]})
        .reset_index()
        .pipe(flatten_columns)
    )

    goodness_overall = (   
        goodness_data
        .query("goodness_score != -1")
        .assign(day_of_week = -1, day_name = "Overall")
        .groupby(["day_of_week", "day_name"])
        .agg({"goodness_score": ["count", "mean", "min", "max"]})
        .reset_index()
        .pipe(flatten_columns)
    )

    goodness_data_per_day = pd.concat([goodness_overall, goodness_per_day], axis=0).reset_index(drop=True)
    return goodness_data_per_day

def get_goodness_range_plot_data(goodness_data_per_day):
    day_name_categories = goodness_data_per_day["day_name"].tolist()[::-1]

    goodness_range_plot_data = (
        goodness_data_per_day
        .assign(
            segment_min = lambda x: np.where(x["goodness_score_min"] == x["goodness_score_max"], x["goodness_score_min"], x["goodness_score_min"] - 0.2),
            segment_max = lambda x: np.where(x["goodness_score_min"] == x["goodness_score_max"], x["goodness_score_max"], x["goodness_score_max"] + 0.2),
            day_name = lambda x: pd.Categorical(x["day_name"], categories=day_name_categories)
        )
    )
    return goodness_range_plot_data

def get_goodness_range_plot_gradient_data(goodness_range_plot_data):
    goodness_range_plot_gradient_data = goodness_range_plot_data.copy()
    goodness_range_plot_gradient_data["segment_seq"] = goodness_range_plot_data.apply(lambda row: list(np.arange(row['segment_min']*10, row['segment_max']*10) / 10), axis=1)

    goodness_range_plot_gradient_data = (
        goodness_range_plot_gradient_data
        .explode("segment_seq")
        .rename(columns={"segment_seq":"segment_seq_min"})
        .assign(segment_seq_min = lambda x: x["segment_seq_min"].astype(float))
        .assign(segment_seq_max = lambda x: x["segment_seq_min"] + 0.1)
        .reset_index(drop=True)
    )
    return goodness_range_plot_gradient_data

def get_activity_data(data):
    activity_columns = ["survey_id", "date", "day_of_week", "day_name", "activity_id", "activity_name", "activity_score"]
    activity_data = (
        data
        .filter(activity_columns, axis=1)
        .drop_duplicates()
        .reset_index(drop=True)
    )
    return activity_data

def get_enjoyment_per_activity(activity_data):
    enjoyment_per_activity = (
        activity_data
        .assign(activity_score = lambda x: np.where(x["activity_score"] == -1, np.nan, x["activity_score"]))
        .groupby(["activity_id", "activity_name"])
        .agg({"activity_name": ["count"], "activity_score": ["mean", "min", "max"]})
        .reset_index()
        .pipe(flatten_columns)
    )
    return enjoyment_per_activity

def get_activity_bar_plot_data(enjoyment_per_activity):
    activity_name_categories = enjoyment_per_activity.sort_values("activity_name_count", ascending=False)["activity_name"].tolist()[::-1]
    activity_frequencies = (
        enjoyment_per_activity
        .assign(activity_name = lambda x: pd.Categorical(x["activity_name"], categories=activity_name_categories))
        .assign(activity_name_prop_of_days = lambda x: x["activity_name_count"]/28)
        .assign(label_location = lambda x: np.where(x["activity_name_count"] < 10, x["activity_name_count"] - 0.5, x["activity_name_count"] - 1))
    )
    return activity_frequencies

def get_activity_list_ordered_by_frequency(activity_frequencies):
    return activity_frequencies.sort_values("activity_name_count", ascending=False)["activity_name"].tolist()[::-1]

def get_activity_range_plot_data(enjoyment_per_activity):
    activity_name_categories = enjoyment_per_activity.sort_values("activity_name_count", ascending=False)["activity_name"].tolist()[::-1]

    activity_range_plot_data = (
        enjoyment_per_activity
        .fillna(-100)
        .assign(
            segment_min = lambda x: np.where(x["activity_score_min"] == x["activity_score_max"], x["activity_score_min"], x["activity_score_min"] - 0.2),
            segment_max = lambda x: np.where(x["activity_score_min"] == x["activity_score_max"], x["activity_score_max"], x["activity_score_max"] + 0.2),
            activity_name = lambda x: pd.Categorical(x["activity_name"], categories=activity_name_categories)
        )
    )
    return activity_range_plot_data

def get_activity_range_plot_gradient_data(activity_range_plot_data):
    activity_range_plot_gradient_data = activity_range_plot_data.copy().query("~segment_min.isna()")
    activity_range_plot_gradient_data["segment_seq"] = activity_range_plot_gradient_data.apply(lambda row: list(np.arange(row['segment_min']*10, row['segment_max']*10) / 10), axis=1)

    activity_range_plot_gradient_data = (
        activity_range_plot_gradient_data
        .explode("segment_seq")
        .rename(columns={"segment_seq":"segment_seq_min"})
        .assign(segment_seq_min = lambda x: x["segment_seq_min"].astype(float))
        .assign(segment_seq_max = lambda x: x["segment_seq_min"] + 0.1)
        .reset_index(drop=True)
    )
    return activity_range_plot_gradient_data

def get_goodness_and_activity_endorsement_data(data):
    goodness_and_activity_endorsments = (
        data
        .filter(["date", "day_of_week", "day_name", "goodness_score", "activity_id"])
        .drop_duplicates()
        .reset_index(drop=True)
        .assign(value = 1)
        .pivot(columns="activity_id", values="value", index=["date", "day_of_week", "day_name", "goodness_score"])
        .fillna(0)
        .reset_index()
        .rename_axis(None, axis=1)
    )
    return goodness_and_activity_endorsments

def get_goodness_and_activity_rating_data(data):
    goodness_and_activity_ratings = (
        data
        .filter(["date", "day_of_week", "day_name", "goodness_score", "activity_id", "activity_score"])
        .drop_duplicates()
        # in case there are duplicate entries for activities, arbitrarily select the first one
        .groupby(["date", "day_of_week", "day_name", "goodness_score", "activity_id"]).activity_score.first()
        .reset_index(drop=False)
        .assign(activity_score = lambda x: x["activity_score"].replace({-1:np.nan}))
        .assign(activity_score_average = lambda x: x.groupby("activity_id")["activity_score"].transform("mean"))
        .assign(activity_score_above_average = lambda x: np.where(x["activity_score"] > x["activity_score_average"], 1, 0))
        .dropna()
        .pivot(columns="activity_id", values="activity_score_above_average", index=["date", "day_of_week", "day_name", "goodness_score"])
        .reset_index()
        .rename_axis(None, axis=1)
    )
    return goodness_and_activity_ratings

def get_activity_occurrence_by_day_of_week_data(data, goodness_and_activity_endorsements, ordered_activities_list):
    non_activity_columns = ["date", "day_of_week", "day_name", "goodness_score"]
    activities_list = [col for col in goodness_and_activity_endorsements.columns.tolist() if not any(match in col for match in non_activity_columns)]
    days_of_week_list = goodness_and_activity_endorsements.sort_values("day_of_week")["day_name"].drop_duplicates().tolist()

    activity_occurrence_by_day_of_week = (
        goodness_and_activity_endorsements
        .groupby("day_name")
        [activities_list]
        .agg("sum")
        .reset_index()
        .melt(id_vars="day_name")
        .rename(columns={"variable":"activity_id", "value":"count"})
        .merge(data[["activity_id", "activity_name"]].drop_duplicates(), how="left", on="activity_id")
        .merge(
            data[["survey_id", "day_name"]].drop_duplicates().groupby("day_name").size().reset_index().rename(columns={0:"n_surveys"}),
            how="left",
            on="day_name"
        )
        .assign(
            percent = lambda x: (x["count"]/x["n_surveys"]*100).round(1),
            day_name = lambda x: pd.Categorical(x["day_name"], categories=days_of_week_list),
            activity_name = lambda x: pd.Categorical(x["activity_name"], categories=ordered_activities_list)
        )
    )
    return activity_occurrence_by_day_of_week

def get_activity_co_occurrence_data(activity_frequencies, goodness_and_activity_endorsements):
    activity_id_to_name = activity_frequencies.set_index("activity_id")["activity_name"].to_dict()
    ordered_activites = activity_frequencies.sort_values("activity_name_count", ascending=False)["activity_name"].tolist()[::-1]

    activity_data_for_co_occur = (
        goodness_and_activity_endorsements
        .drop(columns=["day_of_week", "day_name", "goodness_score"])
        .set_index("date")
    )

    all_co_occur_data = pd.DataFrame()

    activities_for_co_occur = activity_data_for_co_occur.columns.tolist() 
    for activity in activities_for_co_occur:
        row_data = (
            activity_data_for_co_occur[activity_data_for_co_occur[activity] == 1]
            .sum(axis=0)
            .reset_index()
            .rename(columns={"index": "also_did_activity_id", 0:"n_days"})
            .assign(did_activity_id = activity)
            .filter(["did_activity_id", "also_did_activity_id", "n_days"])
        )
        all_co_occur_data = pd.concat([all_co_occur_data, row_data], axis=0).reset_index(drop=True)

    all_co_occur_data = (
        all_co_occur_data
        .replace(activity_id_to_name)
        .rename(columns=lambda x: x.replace("_id", "_name"))
        .merge(
            activity_frequencies[["activity_name", "activity_name_count"]],
            how="left", left_on="did_activity_name", right_on="activity_name"
        )
        .assign(
            percent_days = lambda x: x["n_days"]/x["activity_name_count"],
            did_activity_name = lambda x: pd.Categorical(x["did_activity_name"], categories=ordered_activites),
            also_did_activity_name = lambda x: pd.Categorical(x["also_did_activity_name"], categories=ordered_activites)
        )
        .assign(
            percent_days = lambda x: np.where(x["did_activity_name"] == x["also_did_activity_name"], np.nan, x["percent_days"])
        )
    )
    return all_co_occur_data

def get_activity_clusters(goodness_and_activity_endorsements, activity_frequencies, n_clusters=5):
    data_to_cluster = goodness_and_activity_endorsements.drop(columns=["day_of_week", "day_name", "goodness_score"]).set_index("date")
    model = AgglomerativeClustering(n_clusters=n_clusters, compute_distances=True)
    model = model.fit(data_to_cluster.transpose())

    activity_id_to_name = activity_frequencies[["activity_id", "activity_name", "activity_name_count"]]

    cluster_data = (
        pd.DataFrame({
            "cluster_id": model.labels_.tolist(), 
            "activity_id": data_to_cluster.columns.tolist()
        })
        .merge(activity_id_to_name, how="left", on="activity_id")
        .assign(cluster_size = lambda x: x.groupby("cluster_id")["activity_name"].transform("count"))
        .assign(cluster_child_id = lambda x: x.groupby("cluster_id")["activity_name"].transform("cumcount")*1)
        .assign(activity_name_nchar = lambda x: x["activity_name"].str.len())
        .assign(cluster_child_id_offset = lambda x: x.groupby("cluster_id")["activity_name_nchar"].transform(lambda y: y.shift().cumsum())) #.transform("cumsum"))
        .fillna({"cluster_child_id_offset": 0})
        .assign(activity_start = lambda x: x["cluster_child_id"] + x["cluster_child_id_offset"])
        .assign(activity_end = lambda x: x["activity_start"] + x["activity_name_nchar"])
        .assign(cluster_id = lambda x: x["cluster_id"] + 1)
        .assign(cluster_child_id_centered = lambda x: x.groupby("cluster_id")["cluster_child_id"].transform(lambda y: y-y.mean()))
        .drop(columns="activity_id")
        .sort_values(["cluster_size", "cluster_id"], ascending=False)
        .reset_index(drop=True)
    )
    return cluster_data

def get_goodness_by_activity_range_plot_data(activity_data, goodness_data):
    average_goodness_by_activity = (
        activity_data
        .merge(goodness_data[["survey_id", "goodness_score"]], how="left", on="survey_id")
        .groupby("activity_name")
        .agg({"goodness_score": ["count", "min", "mean", "max"]})
        .reset_index()
        .pipe(flatten_columns)
    )

    activity_name_categories = average_goodness_by_activity.sort_values("goodness_score_mean", ascending=False)["activity_name"].tolist()[::-1]

    goodness_by_activity_range_plot_data = (
        average_goodness_by_activity
        .assign(
            segment_min = lambda x: np.where(x["goodness_score_min"] == x["goodness_score_max"], x["goodness_score_min"], x["goodness_score_min"] - 0.2),
            segment_max = lambda x: np.where(x["goodness_score_min"] == x["goodness_score_max"], x["goodness_score_max"], x["goodness_score_max"] + 0.2),
            activity_name = lambda x: pd.Categorical(x["activity_name"], categories=activity_name_categories)
        )
    )
    return goodness_by_activity_range_plot_data

def get_goodness_by_activity_range_plot_gradient_data(goodness_by_activity_range_plot_data):
    goodness_by_activity_range_plot_gradient_data = goodness_by_activity_range_plot_data.copy().query("~segment_min.isna()")
    goodness_by_activity_range_plot_gradient_data["segment_seq"] = goodness_by_activity_range_plot_gradient_data.apply(lambda row: list(np.arange(row['segment_min']*10, row['segment_max']*10) / 10), axis=1)

    goodness_by_activity_range_plot_gradient_data = (
        goodness_by_activity_range_plot_gradient_data
        .explode("segment_seq")
        .rename(columns={"segment_seq":"segment_seq_min"})
        .assign(segment_seq_min = lambda x: x["segment_seq_min"].astype(float))
        .assign(segment_seq_max = lambda x: x["segment_seq_min"] + 0.1)
        .reset_index(drop=True)
    )
    return goodness_by_activity_range_plot_gradient_data

def get_activity_tile_plot_data(activity_frequencies, goodness_and_activity_endorsements, score_list):
    activity_id_to_name = activity_frequencies.set_index("activity_id")["activity_name"]

    goodness_activity_tile_plot_data = (
        goodness_and_activity_endorsements
        .melt(id_vars=["date", "day_of_week", "day_name", "goodness_score"])
        .merge(activity_id_to_name, how="left", left_on="variable", right_on="activity_id")
        .assign(day_index = lambda x: (x["date"] - x["date"].min()).dt.days)
        .assign(goodness_score = lambda x: pd.Categorical(x["goodness_score"], categories=score_list))
    )
    return goodness_activity_tile_plot_data

def get_activity_lollipop_plot_data(data, goodness_and_activity_endorsments):
    if goodness_and_activity_endorsments.empty:
        lollipop_plot_data = pd.DataFrame(columns=["activity_id", "average_goodness_yes", "average_goodness_no", "percent_difference", "segment_end", "activity_name", "label"])

    else:
        non_activity_columns = ["date", "day_of_week", "day_name", "goodness_score"]
        activities_list = [col for col in goodness_and_activity_endorsments.columns.tolist() if not any(match in col for match in non_activity_columns)]
    
        average_goodness_by_endorsement = pd.DataFrame()
        for activity in activities_list:
            average_goodness_per_activity = (
                goodness_and_activity_endorsments
                .groupby([activity])
                .agg({"goodness_score":"mean"})
                .reset_index()
                .melt(id_vars="goodness_score")
            )
            average_goodness_by_endorsement = pd.concat([average_goodness_by_endorsement, average_goodness_per_activity], axis=0).reset_index(drop=True)

        average_goodness_by_endorsement = (
            average_goodness_by_endorsement
            .pivot(columns="value", values="goodness_score", index="variable")
            .reset_index()
            .rename_axis(None, axis=1)
            .rename(columns={"variable":"activity_id", 0.0:"average_goodness_no", 1.0:"average_goodness_yes"})
        )

        if not "average_goodness_no" in average_goodness_by_endorsement.columns:
            average_goodness_by_endorsement["average_goodness_no"] = np.nan
        if not "average_goodness_yes" in average_goodness_by_endorsement.columns:
            average_goodness_by_endorsement["average_goodness_yes"] = np.nan

        lollipop_plot_data = (
            average_goodness_by_endorsement
            .assign(
                percent_difference = lambda x: ((x["average_goodness_yes"] - x["average_goodness_no"])/x["average_goodness_no"]*100).round(1),
                segment_end=0
            )
            .fillna({"percent_difference": 0})
            .sort_values("percent_difference")
            .merge(data[["activity_id", "activity_name"]].drop_duplicates(), how="left", on="activity_id")
            .assign(
            label = lambda x: x["percent_difference"].astype(str).str.replace("-", "") + "%"
            )
        )

        lollipop_plot_data_activity_cats = lollipop_plot_data["activity_name"].tolist()

        lollipop_plot_data = (
            lollipop_plot_data
            .assign(activity_name = lambda x: pd.Categorical(x["activity_name"], categories=lollipop_plot_data_activity_cats))
            .assign(percent_difference_rescaled = lambda x: rescale_with_midpoint(x["percent_difference"], 0))
        )

    return lollipop_plot_data

def get_rating_scatterplot_data(activity_data, goodness_data):
    rating_scatterplot_data = (
        activity_data
        .assign(activity_score = lambda x: np.where(x["activity_score"] == -1, np.nan, x["activity_score"]))
        .merge(goodness_data[["survey_id", "goodness_score"]], how="left", on="survey_id")
        .reset_index(drop=True)
    )
    return rating_scatterplot_data

def get_correlation_lollipop_plot_data(activity_data, goodness_data, corr_method="spearman"):
    goodness_and_activity_ratings_for_corr = (
        activity_data
        .assign(activity_score = lambda x: np.where(x["activity_score"] == -1, np.nan, x["activity_score"]))
        .merge(goodness_data[["survey_id", "goodness_score"]], how="left", on="survey_id")
        .reset_index(drop=True)
    )

    corr_lollipop_plot_data = (
        goodness_and_activity_ratings_for_corr
        .groupby("activity_name")["activity_score"]
        .corr(goodness_and_activity_ratings_for_corr["goodness_score"], method=corr_method)
        .reset_index()
        .filter(["activity_name", "activity_score"])
        .rename(columns={"activity_score": "r"})
        .fillna(0)
        .sort_values("r", ascending=False)
        .assign(
            segment_end=0,
            label = lambda x: x["r"].round(2).astype(str)
        )
        .sort_values("r")
    )

    corr_lollipop_plot_data_activity_cats = corr_lollipop_plot_data["activity_name"].tolist()

    corr_lollipop_plot_data = (
        corr_lollipop_plot_data
        .assign(activity_name = lambda x: pd.Categorical(x["activity_name"], categories=corr_lollipop_plot_data_activity_cats))
        .assign(r_rescaled = lambda x: rescale_with_midpoint(x["r"], 0))
    )
    return corr_lollipop_plot_data

def get_fitbit_scatterplot_data(fitbit_data, goodness_data, corr_method="spearman"):
    fitbit_scatterplot_data = (
        goodness_data
        .filter(["survey_id", "date", "goodness_score"])
        .merge(fitbit_data[["date", "has_fitbit", "steps", "sleep"]], on=["date"], how="left")
        .fillna({"has_fitbit": 0})
        .query("has_fitbit == 1")
        .reset_index(drop=True)
        .melt(id_vars=["survey_id", "date", "goodness_score", "has_fitbit"])
        .rename(columns={"variable":"fitbit_data_type"})
    )

    fitbit_correlations = (
        fitbit_scatterplot_data
        .groupby("fitbit_data_type")["value"]
        .corr(fitbit_scatterplot_data["goodness_score"], method=corr_method)
        .reset_index()
        .rename(columns={"value": "r"})
        .fillna(0)
        .sort_values("r", ascending=False)
    )

    return fitbit_scatterplot_data, fitbit_correlations