import pandas as pd 
import numpy as np
import plotnine as p9
import matplotlib
import matplotlib.pyplot as plt  

plt.rcParams["figure.dpi"] = 1000

def generate_custom_cmap(pal=["redyellowgreen", "indigo"], cmap_type=["discrete", "continuous"], n_colors=None):
    if pal == "redyellowgreen":
        LOW = "#FF5252"
        MEDIUM = "#FFC108"
        HIGH = "#4CAF50" 
    elif pal == "indigo":
        LOW = "#FFFFFF" #"#E8EAF6"
        MEDIUM = "#5C6BC0" # "#3F51B5"
        HIGH = "#283593" #"#1A237E" 
    else:
        raise ValueError("`pal` must be one of: redyellowgreen, indigo")

    color_list = [LOW, MEDIUM, HIGH]

    if cmap_type == "discrete":
        return plt.cm.colors.LinearSegmentedColormap.from_list("cmap_discrete", color_list, N=n_colors)
    elif cmap_type == "continuous":
        return plt.cm.colors.LinearSegmentedColormap.from_list("cmap_continuous", color_list)
    else:
        raise ValueError("cmap_type must be one of: discrete, continuous")

def get_cmap_hexcodes(cmap, n_colors):
    return [matplotlib.colors.to_hex(cmap(i)) for i in range(n_colors)]

def create_placeholder(placeholder_type=["plot", "table"], width=10):
    if width < 10:
        message = f"Sorry, there were not enough\ndata to create this {placeholder_type}."
    else:
        message = f"Sorry, there were not enough data to create this {placeholder_type}."
    plot = (
        p9.ggplot()
        + p9.geom_text(
            data=pd.DataFrame({"x": [0], "y": [0], "label": [message]}),
            mapping=p9.aes(x="x", y="y", label="label"),
            size=16,
            family="DejaVu Sans",
            fontweight="black"
        )
        + p9.scale_x_continuous(limits=[-1, 1], expand=[0, 0])
        + p9.scale_y_continuous(limits=[-1, 1], expand=[0, 0])
        + p9.theme_void()
        + p9.theme(
            figure_size=(width, 2),
            plot_background=p9.element_rect(fill="white")
        )
    )
    return plot

def create_value_boxes(value_box_data):
    INDIGO = "#3F51B5"
    WIDTH=12
    HEIGHT=2.8
    NROW=3
    NCOL=3

    plot = (
        p9.ggplot(data = value_box_data)
        + p9.geom_rect(
            mapping=p9.aes(xmin="xmin", xmax="xmax",ymin="ymin", ymax="ymax"),
            fill=INDIGO
        )
        + p9.geom_text(
            mapping=p9.aes(x="description_x", y="description_y", label="description"),
            color="white",
            ha="left",
            size=12,
            family="DejaVu Sans",
            fontweight="bold",
            alpha=0.7
        )
        + p9.geom_text(
            mapping=p9.aes(x="value_x", y="value_y", label="value"),
            color="white",
            ha="left",
            size=20,
            family="DejaVu Sans",
            fontweight="bold"
        )
        + p9.facet_wrap("~variable", nrow=NROW, ncol=NCOL)
        + p9.scale_x_continuous(expand=[0, 0])
        + p9.labs(
            x="",
            y="",
            title=""
        )
        + p9.theme_void()
        + p9.theme(
            figure_size=(WIDTH, HEIGHT),
            legend_position="none",
            plot_margin=0,
            panel_spacing_x=0.01,
            panel_spacing_y=0,
            panel_grid_major=p9.element_blank(),
            panel_grid_minor=p9.element_blank(),
            panel_background=p9.element_rect(fill="white"),
            plot_background=p9.element_rect(fill="white"),
            axis_text=p9.element_blank(),
            axis_title=p9.element_blank(),
            axis_ticks=p9.element_blank(),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=14, ha="left"),
            strip_text=p9.element_blank(),
        )
    )
    return plot

def create_goodness_bar_plot(goodness_bar_plot_data, cmap_hexcodes):
    xlims = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
    ylim = goodness_bar_plot_data["n_days"].max()

    if ylim < 5:
        ybreaks = range(0, ylim+1, 1)
        height = 4 
        nudge = 0.05
    else:
        ybreaks = range(0, ylim+1, 2)
        height = 5
        nudge = 0.1

    plot = (
        p9.ggplot()
        + p9.geom_bar(
            data=goodness_bar_plot_data,
            mapping=p9.aes(x="goodness_score", y="n_days", fill="goodness_score"),
            stat="identity",
            width=0.9 
        )
        + p9.geom_text(
            data=goodness_bar_plot_data,
            mapping=p9.aes(x="goodness_score", y="n_days-0.25", label="n_days"),
            family="DejaVu Sans",
            fontweight="bold",
            size=20,
            color="white",
            alpha=0.7,
            nudge_y=-(nudge)
        )
        + p9.scale_y_continuous(expand=[0, 0], breaks=ybreaks)
        + p9.scale_x_discrete(limits=xlims)
        + p9.scale_fill_manual(values=cmap_hexcodes)
        + p9.labs(
            x="Goodness rating",
            y="Number of days"
        )
        + p9.theme_bw()
        + p9.theme(
            figure_size=(10, height),
            legend_position="none",
            panel_grid_major_x=p9.element_blank(),
            panel_grid_minor_x=p9.element_blank(),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=14, ha="left")
        )
    )
    return plot 

def create_goodness_range_plot(goodness_range_plot_data, goodness_range_plot_gradient_data, cmap_hexcodes):
    plot = (
        p9.ggplot()
        + p9.geom_segment(
            data=goodness_range_plot_gradient_data,
            mapping=p9.aes(
                x="segment_seq_min",
                xend="segment_seq_max",
                y="day_name",
                yend="day_name",
                color="segment_seq_min"
            ),
            size=14.2,
            alpha=0.7
        )
        + p9.geom_hline(
            yintercept=7.5,
            linetype="dashed"
        )
        # min 
        + p9.geom_point(
            data=goodness_range_plot_data,
            mapping=p9.aes(
                x="segment_min",
                y="day_name",
                fill="goodness_score_min",
            ),
            size=13,
            stroke=0.3,
            color="black"
        )
        + p9.geom_text(
            data=goodness_range_plot_data.query("goodness_score_min != goodness_score_max"),
            mapping=p9.aes(
                x="segment_min",
                y="day_name",
                label="goodness_score_min"
            ),
            size=11,
            format_string="{:.0f}",
            family="DejaVu Sans",
            color="black"
        )
        # max
        + p9.geom_point(
            data=goodness_range_plot_data,
            mapping=p9.aes(
                x="segment_max",
                y="day_name",
                fill="goodness_score_max",
            ),
            size=13,
            stroke=0.3,
            color="black"
        )
        + p9.geom_text(
            data=goodness_range_plot_data.query("goodness_score_min != goodness_score_max"),
            mapping=p9.aes(
                x="segment_max",
                y="day_name",
                label="goodness_score_max"
            ),
            size=11,
            format_string="{:.0f}",
            family="DejaVu Sans",
            color="black"
        )
        # mean
        + p9.geom_point(
            data=goodness_range_plot_data,
            mapping=p9.aes(
                x="goodness_score_mean",
                y="day_name",
                fill="goodness_score_mean"
            ),
            size=13,
            stroke=0.6,
            color="black"
        )
        + p9.geom_text(
            data=goodness_range_plot_data,
            mapping=p9.aes(
                x="goodness_score_mean",
                y="day_name",
                label="goodness_score_mean"
            ),
            size=11,
            format_string="{:.1f}",
            family="DejaVu Sans",
            color="black"
        )
        + p9.scale_y_discrete(limits=["Sunday", "Saturday", "Friday", "Thursday", "Wednesday", "Tuesday", "Monday", "Overall"])
        + p9.scale_x_continuous(limits=[-1, 11], breaks=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], expand=[0, 0])
        + p9.scale_fill_gradientn(colors=cmap_hexcodes, limits=[0, 10])
        + p9.scale_color_gradientn(colors=cmap_hexcodes, limits=[0, 10])
        + p9.labs(
            x="Goodness rating",
            y="",
            title=""
        )
        + p9.theme_bw()
        + p9.theme(
            figure_size=(10, 5),
            legend_position="none",
            panel_grid_major_y=p9.element_blank(),
            panel_grid_minor_y=p9.element_blank(),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=14, ha="left")
        )
    )
    return plot 

def create_activity_bar_plot(activity_frequencies, cmap_hexcodes):
    ylim = activity_frequencies["activity_name_count"].max()
    height = int(len(activity_frequencies["activity_id"].unique())/2) + 1

    if ylim < 5:
        ybreaks = range(0, ylim+1, 1)
    elif ylim >= 15:
        ybreaks = range(0, ylim+1, 5)
    else:
        ybreaks = range(0, ylim+1, 2)

    plot = (
        p9.ggplot()
        + p9.geom_bar(
            data=activity_frequencies,
            mapping=p9.aes(x="activity_name", y="activity_name_count", fill="activity_name_count"),
            stat="identity" 
        )
        + p9.geom_text(
            data=activity_frequencies,
            mapping=p9.aes(x="activity_name", y="label_location", label="activity_name_count"),
            family="DejaVu Sans",
            fontweight="bold",
            size=20,
            color="white",
            alpha=0.7
        )
        + p9.scale_y_continuous(expand=[0, 0], breaks=ybreaks)
        + p9.scale_fill_gradientn(colors=cmap_hexcodes)
        + p9.labs(
            y="Number of days",
            x=""
        )
        + p9.coord_flip()
        + p9.theme_bw()
        + p9.theme(
            figure_size=(6, height),
            legend_position="none",
            panel_grid_major_y=p9.element_blank(),
            panel_grid_minor_y=p9.element_blank(),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=14, ha="left")
        )
    )
    return plot

def create_activity_range_plot(activity_range_plot_data, activity_range_plot_gradient_data, cmap_hexcodes):
    height = int(len(activity_range_plot_data["activity_id"].unique())/2) + 1

    plot = (  
        p9.ggplot()
        + p9.geom_segment(
            data=activity_range_plot_gradient_data,
            mapping=p9.aes(
                x="segment_seq_min",
                xend="segment_seq_max",
                y="activity_name",
                yend="activity_name",
                color="segment_seq_min"
            ),
            size=14.2,
            alpha=0.7
        )
        + p9.geom_point(
            data=activity_range_plot_data,
            mapping=p9.aes(
                x="segment_min",
                y="activity_name",
                fill="activity_score_min",
            ),
            size=13,
            stroke=0.3,
            color="black"
        )
        + p9.geom_point(
            data=activity_range_plot_data,
            mapping=p9.aes(
                x="segment_max",
                y="activity_name",
                fill="activity_score_max",
            ),
            size=13,
            stroke=0.3,
            color="black"
        )
        + p9.geom_text(
            data=activity_range_plot_data.query("activity_score_min != activity_score_max"),
            mapping=p9.aes(
                x="segment_min",
                y="activity_name",
                label="activity_score_min"
            ),
            size=11,
            format_string="{:.0f}",
            family="DejaVu Sans",
            color="black"
        )
        + p9.geom_text(
            data=activity_range_plot_data.query("activity_score_min != activity_score_max"),
            mapping=p9.aes(
                x="segment_max",
                y="activity_name",
                label="activity_score_max"
            ),
            size=11,
            format_string="{:.0f}",
            family="DejaVu Sans",
            color="black"
        )
        + p9.geom_point(
            data=activity_range_plot_data,
            mapping=p9.aes(
                x="activity_score_mean",
                y="activity_name",
                fill="activity_score_mean"
            ),
            size=13,
            stroke=0.6,
            color="black"
        )
        + p9.geom_text(
            data=activity_range_plot_data,
            mapping=p9.aes(
                x="activity_score_mean",
                y="activity_name",
                label="activity_score_mean"
            ),
            size=11,
            format_string="{:.1f}",
            family="DejaVu Sans",
            color="black"
        )
        + p9.scale_x_continuous(limits=[-1, 11], breaks=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], expand=[0,0])
        + p9.scale_y_discrete(labels=False)
        + p9.scale_fill_gradientn(colors=cmap_hexcodes, limits=[0, 10])
        + p9.scale_color_gradientn(colors=cmap_hexcodes, limits=[0, 10])
        + p9.labs(
            x="Activity rating",
            y="",
            title=""
        )
        + p9.theme_bw()
        + p9.theme(
            figure_size=(6, height),
            legend_position="none",
            panel_grid_major_y=p9.element_blank(),
            panel_grid_minor_y=p9.element_blank(),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=14, ha="left")
        )
    )
    return plot

def create_activity_occurrence_by_day_of_week_heatmap(activity_occurrence_by_day_of_week_data, cmap_hexcodes):
    plot = (
        p9.ggplot(data=activity_occurrence_by_day_of_week_data)
        + p9.geom_tile(
            mapping=p9.aes(y="activity_name", x="day_name", fill="percent"),
            color="black"
        )
        + p9.scale_x_discrete(expand=[0, 0])
        + p9.scale_y_discrete(expand=[0, 0])
        + p9.scale_fill_gradientn(colors=cmap_hexcodes, na_value="grey")
        + p9.labs(
            x="",
            y=""
        )
        + p9.theme_bw()
        + p9.theme(
            figure_size=(10, 5),
            legend_position="none",
            panel_grid_major_y=p9.element_blank(),
            panel_grid_minor_y=p9.element_blank(),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=14, ha="left")
        )
    )
    return plot

def create_activity_co_occurrence_heatmap(data, cmap_hexcodes):
    plot = (
        p9.ggplot(data=data)
        + p9.geom_tile(
            mapping=p9.aes(x="also_did_activity_name", y="did_activity_name", fill="percent_days"),
            color="black"
        )
        + p9.coord_equal()
        + p9.scale_x_discrete(expand=[0, 0])
        + p9.scale_y_discrete(expand=[0, 0])
        + p9.scale_fill_gradientn(colors=cmap_hexcodes, na_value="grey")
        + p9.labs(
            x="",
            y=""
        )
        + p9.theme_bw()
        + p9.theme(
            figure_size=(9, 8),
            legend_position="none",
            panel_grid_major_y=p9.element_blank(),
            panel_grid_minor_y=p9.element_blank(),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_text_x=p9.element_text(angle=45, hjust=1),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=14, ha="left"),
            plot_margin=0
        )
    )
    return plot

def create_activity_cluster_plot(cluster_data, cmap_hexcodes, fill_var="cluster_id"):
    plot = (
        p9.ggplot(data=cluster_data)
        + p9.geom_label(
            mapping=p9.aes(y="cluster_child_id_centered", x="cluster_id", label="activity_name", fill=fill_var),
            ha="center",
            label_padding=0.5,
            boxstyle="round",
            family="DejaVu Sans",
            color="black",
            size=10
        )
        + p9.scale_x_continuous(limits=[0.5, 5.5])
        + p9.scale_y_continuous(expand=(0, 0.5, 0, 0.5))
        + p9.scale_fill_gradientn(colors=cmap_hexcodes)
        + p9.labs(
            x="Activity cluster",
            y=""
        )
        + p9.theme_bw()
        + p9.theme(
            figure_size=(10, 3),
            legend_position="none",
            panel_grid_major=p9.element_blank(),
            panel_grid_minor=p9.element_blank(),
            axis_text_x=p9.element_text(family="DejaVu Sans", size=12),
            axis_text_y=p9.element_text(family="DejaVu Sans", size=1, color="white"),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks_x=p9.element_line(color="white"),
            axis_ticks_y=p9.element_blank(),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=12, ha="left")
        )
    )   
    return plot

def create_goodness_legend_plot(score_list, cmap_hexcodes):
    plot = (
        p9.ggplot(
            data=pd.DataFrame({"score":score_list,"name":"Goodness rating"}).assign(score = lambda x: pd.Categorical(x["score"], categories=score_list))
        )
        + p9.geom_tile(
            mapping=p9.aes(x="score", y="name", fill="score")
        )
        + p9.geom_text(
            mapping=p9.aes(x="score", y="name", label="score"),
            family="DejaVu Sans",
            fontweight="bold",
            size=10
        )
        + p9.scale_y_discrete(expand=[0, 0])
        + p9.scale_x_discrete(expand=[0, 0], labels=False)
        + p9.scale_fill_manual(values=cmap_hexcodes, na_value="white")
        + p9.labs(
            x="",
            y=""
        )
        + p9.theme_bw()
        + p9.theme(
            figure_size=(6, 0.25),
            legend_position="none",
            legend_text=p9.element_text(family="DejaVu Sans"),
            legend_title=p9.element_text(family="DejaVu Sans", va="baseline", size=12),
            panel_grid_major_y=p9.element_blank(),
            panel_grid_minor_y=p9.element_blank(),
            axis_text=p9.element_text(family="DejaVu Sans", size=10),
            axis_title=p9.element_text(family="DejaVu Sans", size=10, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=14, ha="left"),
            plot_margin_bottom=0
        )
    )
    return plot

def create_activity_tile_plot(goodness_activity_tile_plot_data, ordered_activities_list, cmap_hexcodes, include_legend=False):
    plot = (
        p9.ggplot(data=goodness_activity_tile_plot_data)
        + p9.geom_tile(
            mapping=p9.aes(x="day_index", y="activity_name", fill="goodness_score")
        )
        + p9.geom_point(
            data=goodness_activity_tile_plot_data.query("value == 1"),
            mapping=p9.aes(x="day_index", y="activity_name"),
            shape="*",
            size=4
        )
        + p9.geom_hline(
            yintercept=[i + 0.5 for i in range(0, len(ordered_activities_list))]
        )
        + p9.scale_y_discrete(expand=[0, 0])
        + p9.scale_x_continuous(breaks=[0, 7, 14, 21, 28], expand=[0, 0])
        + p9.scale_fill_manual(values=cmap_hexcodes, na_value="white")
        + p9.guides(
            fill=p9.guide_legend(nrow=1)
        )
        + p9.labs(
            x="Study day",
            y="",
            fill="Goodness rating"
        )
        + p9.theme_bw()
    )
    if include_legend:
        plot = plot + p9.theme(
            figure_size=(10, 7),
            legend_position="top",
            legend_direction="horizontal",
            legend_key_spacing=0,
            legend_box_margin=2,
            legend_box_spacing=0,
            legend_text_position="bottom",
            legend_background=p9.element_blank(),
            legend_box=p9.element_blank(),
            legend_text=p9.element_text(family="DejaVu Sans"),
            legend_title=p9.element_text(family="DejaVu Sans", va="baseline", size=12),
            panel_grid_major_y=p9.element_blank(),
            panel_grid_minor_y=p9.element_blank(),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=14, ha="left")
        )
    else: 
        plot = plot + p9.theme(
            figure_size=(10, 6),
            legend_position="none",
            panel_grid_major_y=p9.element_blank(),
            panel_grid_minor_y=p9.element_blank(),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=14, ha="left")
        )
    return plot

def create_goodness_by_activity_range_plot(goodness_by_activity_range_plot_gradient_data, goodness_by_activity_range_plot_data, cmap_hexcodes):
    height = int(len(goodness_by_activity_range_plot_data["activity_name"].unique())/2) + 1
    plot = (   
        p9.ggplot()
        + p9.geom_segment(
            data=goodness_by_activity_range_plot_gradient_data,
            mapping=p9.aes(
                x="segment_seq_min",
                xend="segment_seq_max",
                y="activity_name",
                yend="activity_name",
                color="segment_seq_min"
            ),
            size=14.2,
            alpha=0.7
        )
        + p9.geom_point(
            data=goodness_by_activity_range_plot_data,
            mapping=p9.aes(
                x="segment_min",
                y="activity_name",
                fill="goodness_score_min",
            ),
            size=13,
            stroke=0.3,
            color="black"
        )
        + p9.geom_point(
            data=goodness_by_activity_range_plot_data,
            mapping=p9.aes(
                x="segment_max",
                y="activity_name",
                fill="goodness_score_max",
            ),
            size=13,
            stroke=0.3,
            color="black"
        )
        + p9.geom_text(
            data=goodness_by_activity_range_plot_data.query("goodness_score_min != goodness_score_max"),
            mapping=p9.aes(
                x="segment_min",
                y="activity_name",
                label="goodness_score_min"
            ),
            size=11,
            format_string="{:.0f}",
            family="DejaVu Sans",
            color="black"
        )
        + p9.geom_text(
            data=goodness_by_activity_range_plot_data.query("goodness_score_min != goodness_score_max"),
            mapping=p9.aes(
                x="segment_max",
                y="activity_name",
                label="goodness_score_max"
            ),
            size=11,
            format_string="{:.0f}",
            family="DejaVu Sans",
            color="black"
        )
        + p9.geom_point(
            data=goodness_by_activity_range_plot_data,
            mapping=p9.aes(
                x="goodness_score_mean",
                y="activity_name",
                fill="goodness_score_mean"
            ),
            size=13,
            stroke=0.6,
            color="black"
        )
        + p9.geom_text(
            data=goodness_by_activity_range_plot_data,
            mapping=p9.aes(
                x="goodness_score_mean",
                y="activity_name",
                label="goodness_score_mean"
            ),
            size=11,
            format_string="{:.1f}",
            family="DejaVu Sans",
            color="black"
        )
        + p9.scale_x_continuous(limits=[-1, 11], breaks=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], expand=[0,0])
        + p9.scale_y_discrete()
        + p9.scale_fill_gradientn(colors=cmap_hexcodes, limits=[0, 10])
        + p9.scale_color_gradientn(colors=cmap_hexcodes, limits=[0, 10])
        + p9.labs(
            x="Goodness rating",
            y="",
            title=""
        )
        + p9.theme_bw()
        + p9.theme(
            figure_size=(10, height),
            legend_position="none",
            panel_grid_major_y=p9.element_blank(),
            panel_grid_minor_y=p9.element_blank(),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=14, ha="left")
        )
    )
    return plot

def create_activity_lollipop_plot(lollipop_plot_data, cmap_hexcodes, plot_title=""):
    height = int(len(lollipop_plot_data["activity_name"].unique())/2) + 2
    plot = (
        p9.ggplot(data=lollipop_plot_data)
        + p9.geom_vline(
            xintercept=0,
            color="black",
            linetype="dashed"
        )
        + p9.geom_segment(
            mapping=p9.aes(x="percent_difference", xend="segment_end", y="activity_name", yend="activity_name", color="percent_difference_rescaled"),
            size=8
        )
        + p9.geom_point(
            mapping=p9.aes(x="percent_difference", y="activity_name", fill="percent_difference_rescaled"),
            size=19,
            color="black",
            stroke=0.5
        ) 
        + p9.geom_text(
            mapping=p9.aes(x="percent_difference", y="activity_name", label="label"),
            size=9,
            family="DejaVu Sans",
            color="black"
        )
        + p9.scale_color_gradientn(colors=cmap_hexcodes, limits=[0, 1])
        + p9.scale_fill_gradientn(colors=cmap_hexcodes, limits=[0, 1])
        + p9.labs(
            x="Percent difference in average same-day goodness rating",
            y="",
            title=plot_title
        )
        + p9.theme_bw()
        + p9.theme(
            figure_size=(10, height),
            legend_position="none",
            panel_grid_major_y=p9.element_blank(),
            panel_grid_minor_y=p9.element_blank(),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=12, ha="left")
        )
    )
    return plot

def create_rating_scatterplot(rating_scatterplot_data, cmap_hexcodes):
    plot = (
        p9.ggplot(data=rating_scatterplot_data.dropna())
        + p9.geom_point(
            mapping=p9.aes(x="goodness_score", y="activity_score", color="goodness_score"),
            size=5,
            alpha=0.7
        )
        + p9.facet_wrap("~activity_name", ncol=4)
        + p9.scale_x_continuous(limits=[0, 10], breaks=[0, 2, 4, 6, 8, 10], expand=[0, 1, 0, 1])
        + p9.scale_y_continuous(limits=[0, 10], breaks=[0, 2, 4, 6, 8, 10], expand=[0, 1, 0, 1])
        + p9.scale_color_gradientn(colors=cmap_hexcodes)
        + p9.labs(
            x="Goodness rating",
            y="Activity rating"
        )
        + p9.theme_bw()
        + p9.theme(
            figure_size=(10, 10),
            legend_position="none",
            panel_grid_minor=p9.element_blank(),
            strip_text=p9.element_text(family="DejaVu Sans", size=10, face="bold", color="white"),
            strip_background=p9.element_rect(fill="#3F51B5"),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=12, ha="left")
        )
    )
    return plot

def create_rating_scatterplot_with_correlations(rating_scatterplot_data, corr_lollipop_plot_data, cmap_hexcodes):
    scatterplot_activities = rating_scatterplot_data.dropna()["activity_name"].drop_duplicates().tolist()

    n_facets = len(rating_scatterplot_data[["activity_id", "activity_score"]].dropna()["activity_id"].unique())
    if n_facets <= 4:
        height = 3
    elif (n_facets > 4) & (n_facets % 4 == 0):
        height = int(n_facets/4) * 2
    else:
        height = (int(n_facets/4) + 1) * 2

    scatterplot_annotations = (
        corr_lollipop_plot_data
        .filter(["activity_name", "r"], axis=1)
        .query("activity_name in @scatterplot_activities")
        .assign(
            r_cat = lambda x: x["r"].case_when([
                (x["r"] == 0, np.nan), 
                (x["r"] < 0, 0),
                (x["r"] > 0, 10),
            ]),
            label = lambda x: "r=" + x["r"].round(2).astype(str),
            x = 0,
            y = 0
        )
    )

    plot = (
        p9.ggplot(data=rating_scatterplot_data.dropna())
        + p9.geom_point(
            mapping=p9.aes(x="goodness_score", y="activity_score", color="goodness_score"),
            size=5,
            alpha=0.7
        )
        + p9.geom_text(
            data = scatterplot_annotations,
            mapping = p9.aes(x="x", y="y", label="label", color="r_cat"),
            parse=True,
            ha="left",
            nudge_y=-0.5,
            nudge_x=-0.5,
            family="DejaVu Sans"
        )
        + p9.facet_wrap("activity_name", ncol=4)
        + p9.scale_x_continuous(limits=[-0.5, 10.5], breaks=[0, 2, 4, 6, 8, 10], expand=[0, 0.5, 0, 0.5])
        + p9.scale_y_continuous(limits=[-0.5, 10.5], breaks=[0, 2, 4, 6, 8, 10], expand=[0, 0.5, 0, 0.5])
        + p9.scale_color_gradientn(colors=cmap_hexcodes, na_value="grey")
        + p9.labs(
            x="Goodness rating",
            y="Activity rating"
        )
        + p9.theme_bw()
        + p9.theme(
            figure_size=(10, height),
            legend_position="none",
            panel_grid_minor=p9.element_blank(),
            strip_text=p9.element_text(family="DejaVu Sans", size=10, face="bold", color="white"),
            strip_background=p9.element_rect(fill="#3F51B5"),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=12, ha="left")
        )
    )
    return plot

def create_correlation_lollipop_plot(corr_lollipop_plot_data, cmap_hexcodes, corr_method="Spearman"):
    plot = (
        p9.ggplot(data=corr_lollipop_plot_data)
        + p9.geom_vline(
            xintercept=0,
            color="black",
            linetype="dashed"
        )
        + p9.geom_segment(
            mapping=p9.aes(x="r", xend="segment_end", y="activity_name", yend="activity_name", color="r_rescaled"),
            size=8
        )
        + p9.geom_point(
            mapping=p9.aes(x="r", y="activity_name", fill="r_rescaled"),
            size=19,
            color="black",
            stroke=0.5
        ) 
        + p9.geom_text(
            mapping=p9.aes(x="r", y="activity_name", label="label"),
            size=10,
            family="DejaVu Sans",
            color="black"
        )
        + p9.scale_x_continuous(breaks=[-1, -0.5, 0, 0.5, 1])
        + p9.scale_color_gradientn(colors=cmap_hexcodes)
        + p9.scale_fill_gradientn(colors=cmap_hexcodes)
        + p9.labs(
            x=f"{corr_method} correlation between activity rating and same-day goodness rating",
            y=""
        )
        + p9.theme_bw()
        + p9.theme(
            figure_size=(10, 11),
            legend_position="none",
            panel_grid_major_y=p9.element_blank(),
            panel_grid_minor_y=p9.element_blank(),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=14, ha="left")
        )
    )
    return plot

def create_fitbit_scatterplot(fitbit_scatterplot_data, fitbit_correlations, cmap_hexcodes):
    HEIGHT = 4

    fitbit_data_type_to_title = {
        "steps":"Steps",
        "sleep":"Hours of sleep"
    }

    scatterplot_annotations = (
        fitbit_correlations
        .assign(
            r_cat = lambda x: x["r"].case_when([
                (x["r"] == 0, np.nan), 
                (x["r"] < 0, 0),
                (x["r"] > 0, 10),
            ]),
            label = lambda x: "r=" + x["r"].round(2).astype(str),
            x = 0,
            y = 0
        )
    )

    plot = (
        p9.ggplot(data=fitbit_scatterplot_data.replace(fitbit_data_type_to_title).dropna())
        + p9.geom_point(
            mapping=p9.aes(x="goodness_score", y="value", color="goodness_score"),
            size=5,
            alpha=0.7
        )
        + p9.geom_text(
            data = scatterplot_annotations.replace(fitbit_data_type_to_title),
            mapping = p9.aes(x="x", y="y", label="label", color="r_cat"),
            parse=True,
            ha="left",
            nudge_y=-0.5,
            nudge_x=-0.5,
            family="DejaVu Sans"
        )
        + p9.facet_wrap("fitbit_data_type", scales="free_y", ncol=2)
        + p9.scale_x_continuous(limits=[-0.5, 10.5], breaks=[0, 2, 4, 6, 8, 10], expand=[0, 0.5, 0, 0.5])
        + p9.scale_y_continuous(labels=lambda y: [f"{i:,}".replace(".0", "") for i in y])
        + p9.scale_color_gradientn(colors=cmap_hexcodes, na_value="grey")
        + p9.labs(
            x="Goodness rating",
            y="Fitbit measurement"
        )
        + p9.theme_bw()
        + p9.theme(
            figure_size=(10, HEIGHT),
            legend_position="none",
            panel_grid_minor=p9.element_blank(),
            strip_text=p9.element_text(family="DejaVu Sans", size=10, face="bold", color="white"),
            strip_background=p9.element_rect(fill="#3F51B5"),
            axis_text=p9.element_text(family="DejaVu Sans", size=12),
            axis_title=p9.element_text(family="DejaVu Sans", size=12, face="bold"),
            axis_ticks=p9.element_line(color="white"),
            plot_title=p9.element_text(family="DejaVu Sans", face="bold", size=12, ha="left")
        )
    )
    return plot