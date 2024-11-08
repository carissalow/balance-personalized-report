import pandas as pd 
import numpy as np
from great_tables import *

def create_activity_day_of_week_table(activity_data, activity_frequencies, activity_occurrence_by_day_of_week_data, ordered_activities_list):
    day_of_week_columns = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    n_surveys = len(activity_data["survey_id"].drop_duplicates())
    constant_activities = activity_frequencies.query("activity_name_count == @n_surveys")["activity_name"].tolist()

    activity_by_day = (
        activity_occurrence_by_day_of_week_data
        .assign(
            day_name = lambda x: x["day_name"].astype("object"),
            activity_name = lambda x: x["activity_name"].astype("object"),
            percent = lambda x: x["percent"].round(0).astype("int")
        )
        .filter(["day_name", "activity_name", "percent"])
        .pivot(columns="day_name", values="percent", index="activity_name")
        .reset_index()
        .pipe(lambda x: pd.concat([pd.DataFrame(columns=day_of_week_columns), x], axis=0))
        .rename(columns={"activity_name":"Activity"})
        .filter(["Activity"] + day_of_week_columns)
        .query("Activity not in @constant_activities")
        .reset_index(drop=True)
        .assign(Activity = lambda x: pd.Categorical(x["Activity"], categories=ordered_activities_list[::-1]))
        .sort_values("Activity")
        .reset_index(drop=True)
        .assign(Activity = lambda x: x["Activity"].astype("object"))
    )

    data_color_palette = ["#283593","#5C6BC0","#FFFFFF"]

    table = (
        GT(activity_by_day)
        .opt_table_font(font=google_font("Source Sans 3"))
        .data_color(
            palette=data_color_palette, 
            na_color="white",
            reverse=True,
            columns=day_of_week_columns, 
            domain=[0, 100]
        )
        .tab_style(
            style=style.borders(sides=["right"], color="#D3D3D3", weight="1px"),
            locations=loc.body(columns=["Activity"])
        )
        .tab_options(
            table_width="100%",
            table_layout="auto",
            table_body_hlines_color="#D3D3D3",
            table_font_size="16px",
            column_labels_font_weight=700,
            column_labels_font_size="18px",
            column_labels_border_bottom_color="#D3D3D3"
        )
    )
    return table



def create_related_activities_table(activity_data, activity_frequencies, activity_co_occurrence_data, ordered_activities_list, cmap_hexcodes):
    n_surveys = len(activity_data["survey_id"].drop_duplicates())
    constant_activities = activity_frequencies.query("activity_name_count == @n_surveys")["activity_name"].tolist()

    related_activities_data = (
        activity_co_occurrence_data
        .dropna()
        .query("also_did_activity_name not in @constant_activities")
        .query("activity_name not in @constant_activities")
        .assign(
            freq_group = lambda x: x["percent_days"].case_when([
                (x["percent_days"] == 0, "Never"),
                ((x["percent_days"] > 0) & (x["percent_days"] < 0.33), "Rarely"),
                ((x["percent_days"] >= 0.33) & (x["percent_days"] < 0.66), "Sometimes"),
                ((x["percent_days"] >= 0.66) & (x["percent_days"] < 1), "Often"),
                (x["percent_days"] == 1, "Always")
            ])
        )
        .sort_values(["did_activity_name", "freq_group", "percent_days"], ascending=False)
        .groupby(["did_activity_name", "freq_group"], observed=False)["also_did_activity_name"].apply(lambda x: ', '.join(map(str, x)))
        .reset_index()
        .dropna()
        .assign(did_activity_name = lambda x: pd.Categorical(x["did_activity_name"], categories=ordered_activities_list[::-1]))
        .assign(freq_group = lambda x: pd.Categorical(x["freq_group"], categories=["Always", "Often", "Sometimes", "Rarely", "Never"]))
        .sort_values(["did_activity_name", "freq_group"])
        .reset_index(drop=True)
        .rename(columns={
            "did_activity_name":"Activity",
            "freq_group":"Frequency",
            "also_did_activity_name":"Related activities"
        })
        .assign(Activity = lambda x: np.where(x["Activity"] == x["Activity"].shift(), "", x["Activity"]))
    )

    always_rows = related_activities_data.query("Frequency == 'Always'").index.tolist()
    often_rows = related_activities_data.query("Frequency == 'Often'").index.tolist()
    sometimes_rows = related_activities_data.query("Frequency == 'Sometimes'").index.tolist()
    rarely_rows = related_activities_data.query("Frequency == 'Rarely'").index.tolist()
    never_rows = related_activities_data.query("Frequency == 'Never'").index.tolist()

    activity_rows = related_activities_data.query("Activity != ''").index.tolist()

    table = (
        GT(related_activities_data)
        .opt_table_font(font=google_font("Source Sans 3"))
        .tab_style(
            style=style.fill(color=cmap_hexcodes[0]),
            locations=loc.body(rows=never_rows, columns=["Frequency", "Related activities"])
        )
        .tab_style(
            style=style.fill(color=cmap_hexcodes[1]),
            locations=loc.body(rows=rarely_rows, columns=["Frequency", "Related activities"])
        )
        .tab_style(
            style=style.fill(color=cmap_hexcodes[2]),
            locations=loc.body(rows=sometimes_rows, columns=["Frequency", "Related activities"])
        )
        .tab_style(
            style=style.fill(color=cmap_hexcodes[3]),
            locations=loc.body(rows=often_rows, columns=["Frequency", "Related activities"])
        )
        .tab_style(
            style=style.fill(color=cmap_hexcodes[4]),
            locations=loc.body(rows=always_rows, columns=["Frequency", "Related activities"])
        )
        .tab_style(
            style=style.borders(sides=["left"], color="#D3D3D3", weight="1px"),
            locations=loc.body(columns=["Frequency", "Related activities"])
        )
        #.tab_style(
        #    style=style.text(size="16px", weight="bold"),
        #    locations=loc.body(columns=["Activity", "Frequency"]),
        #)
        .tab_style(
            style=style.borders(sides="top", color="#D3D3D3", weight="1px"),
            locations=loc.body(rows=activity_rows)
        )
        .tab_options(
            table_width="100%",
            table_layout="auto",
            container_height="600px",
            container_overflow_y="True",
            table_body_hlines_color="white",
            table_body_hlines_width="0px",
            column_labels_font_weight=700,
            table_font_size="16px",
            column_labels_font_size="18px",
            column_labels_border_bottom_color="#D3D3D3"
        )
    )
    return table