import polars as pl
import ff_functions as ff
import matplotlib.pyplot as plt
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
import nflreadpy as nfl

def generate_qb_performance_table(week: int):
    qb_stats = ff.get_qb_stats()
    qb_stats = qb_stats.filter(pl.col("week") == week).sort(pl.col("ff_points_total"), descending=True)
    table_data = [
        ["QB", "Team", "Pass Yards \n (%25)", "Pass TDs \n (4)", "INTs \n (-2)", "Rush Yards \n (%10)", "Rush TDs \n (6)", "ff_points_total"]
    ]
    for i in range(10):
        row = qb_stats[i]
        qb = row["short_name"].item()
        team = row["team"].item()
        pass_yards = row["pass_yards"].item()
        pass_tds = row["pass_touchdowns"].item()
        ints = row["interceptions"].item()
        rush_yards = row["rushing_yards"].item()
        rush_tds = row["rushing_tds"].item()
        ff_total = row["ff_points_total"].item()
        table_data.append([qb, team, pass_yards, pass_tds, ints, rush_yards, rush_tds, ff_total])
    table = Table(
            table_data,
            colWidths=[2*cm, 1.2*cm, 2.2*cm, 2.2*cm, 2*cm, 2.5*cm, 2.5*cm],
            rowHeights=[1.2*cm] * len(table_data)
        )
    
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("VALIGN", (0,1), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"), # komplette Tabelle inkl. Kopfzeile zentrieren
        ("ALIGN", (0,0), (1,-1), "LEFT"), # erste zwei Spalten explizit nach links
    ]))
    return table

def generate_qb_season_ff(week: int):
    k = 10  # Anzahl der Top-Kicker, die angezeigt werden sollen
    qb_top_k = (
        ff.get_qb_stats()
        .filter(pl.col("week") <= week)
        .select(['ff_points_total', 'short_name', 'player_id'])
        .group_by("player_id")
        .agg(pl.col("ff_points_total").sum().alias("ff_points_total_season"))
        .sort("ff_points_total_season", descending=True)
    )[:k, :]

    qb_top_k = qb_top_k.join(
        other=ff.get_qb_stats()
                .filter(pl.col("week") <= week)
                .select(['player_id', 
                         'short_name', 
                         'team', 
                         'week', 
                         'ff_points_total']),
        how='inner',
        on='player_id',
        suffix='_game'
    )

    # 1. Kumulierte Punkte berechnen
    df_cum = (
        qb_top_k
        .sort(["player_id", "week"])
        .with_columns(
            pl.col("ff_points_total")
            .cum_sum()
            .over("player_id")
            .alias("cum_points")
        )
    )
    sorted_names = df_cum["short_name"].unique().to_list()

    # 3. Für Matplotlib in Pandas umwandeln
    pdf = df_cum.to_pandas()

    fig, axs = plt.subplots(figsize=[12,8])
    team_color_map = (
    nfl.load_teams()
        .select(["team_abbr", "team_color"])
        .to_dict(as_series=False)
    )

    team_color_map = dict(zip(
        team_color_map["team_abbr"],
        team_color_map["team_color"]
    ))
    markers = ["o", "s", "D", "^", "v", "P", "X", "*"]
    linestyles = ["-", "--", "-.", ":"]

    handles = []
    labels = []
    for i, name in enumerate(sorted_names):
        group = pdf[pdf["short_name"] == name]

        team = group["team"].iloc[0]
        color = team_color_map.get(team, "black")
        marker = markers[i % len(markers)]
        linestyle = linestyles[i % len(linestyles)]

        line, = plt.plot(
            group["week"],
            group["cum_points"],
            marker=marker,
            linestyle=linestyle,
            color=color,
            linewidth=2,
            markersize=7,
        )

        handles.append(line)
        labels.append(f"{name} ({team})")

    axs.set_ylabel("Kumulierte FF Total Points")
    axs.set_title("QB – Kumulierte Fantasy-Punkte")
    axs.legend(handles, labels, loc="upper left")
    axs.grid(True)

    fig.tight_layout()
    fig.savefig(f"plots/qb/qb_season_performance_week_{week}.png")

def generate_qb_ff_plots(week: int):
    df_qb = ff.get_qb_stats().filter(pl.col("week") <= week)
    fig, axs = plt.subplots(nrows=3, ncols=2, figsize=[12, 8])

    # Totale Punktzahl
    axs[0, 0].boxplot(df_qb["ff_points_total"].to_list(), notch=True)
    axs[0, 0].set_title('ff_points_total')
    axs[0, 0].grid()

    axs[0, 1].axis('off')  # Leeres Subplot für die zweite Spalte der ersten Zeile
    # Passing 
    axs[1, 0].boxplot(df_qb["ff_points_passing_yards"].to_list(), notch=True)
    axs[1, 0].set_title('ff Passing Yards')
    axs[1, 0].grid()

    axs[1, 1].boxplot(df_qb["ff_points_passing_tds"].to_list(), notch=True)
    axs[1, 1].set_title('ff Passing TDs')
    axs[1, 1].grid()

    # Rushing
    axs[2, 0].boxplot(df_qb["ff_points_rushing_yards"].to_list(), notch=True)
    axs[2, 0].set_title('ff Rushing Yards')
    axs[2, 0].grid()

    axs[2, 1].boxplot(df_qb["ff_points_rushing_tds"].to_list(), notch=True)
    axs[2, 1].set_title('ff Rushing TDs')
    axs[2, 1].grid()

    fig.suptitle(f"QB – Fantasy-Punkte bis Woche {week}")
    fig.tight_layout()
    fig.savefig(f"plots/qb/qb_ff_plots_week_{week}.png")