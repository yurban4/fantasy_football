import polars as pl
import ff_functions as ff
import matplotlib.pyplot as plt
import nflreadpy as nfl
from reportlab.platypus import Table, TableStyle, Image, PageBreak
from reportlab.lib.units import cm
from reportlab.lib import colors

def generate_rb_performance_table(week: int):
    rb_stats = ff.get_rb_stats()
    rb_stats = rb_stats.filter(pl.col("week") == week).sort(pl.col("ff_points_total"), descending=True)
    table_data = [
        ["RB", "Team", "Rush Yards \n (%10)", "Rush TDs \n (6)", "Receptions", "Rec Yards \n (%10)", "Rec TDs \n (6)", "ff_points_total"]
    ]
    for i in range(10):
        row = rb_stats[i]
        rb = row["short_name"].item()
        team = row["team"].item()
        rush_yards = row["rushing_yards"].item()
        rush_tds = row["rushing_tds"].item()
        receptions = row["receptions"].item()
        rec_yards = row["receiving_yards"].item()
        rec_tds = row["receiving_tds"].item()
        ff_total = row["ff_points_total"].item()
        table_data.append([rb, team, rush_yards, rush_tds, receptions, rec_yards, rec_tds, ff_total])
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


def generate_rb_season_ff(week: int):
    k = 10  # Anzahl der Top-Kicker, die angezeigt werden sollen
    rb_top_k = (
        ff.get_rb_stats()
        .filter(pl.col("week") <= week)
        .select(['ff_points_total', 'short_name', 'player_id'])
        .group_by("player_id")
        .agg(pl.col("ff_points_total").sum().alias("ff_points_total_season"))
        .sort("ff_points_total_season", descending=True)
    )[:k, :]

    rb_top_k = rb_top_k.join(
        other=ff.get_rb_stats()
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
        rb_top_k
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
    axs.set_title("RB – Kumulierte Fantasy-Punkte")
    axs.legend(handles, labels, loc="upper left")
    axs.grid(True)

    fig.tight_layout()
    fig.savefig(f"plots/rb/rb_season_performance_week_{week}.png")

def generate_rb_ff_plots(week: int):
    df_rb = ff.get_rb_stats().filter(pl.col("week") <= week)
    fig, axs = plt.subplots(nrows=3, ncols=2, figsize=[12, 8])

    # Totale Punktzahl
    axs[0, 0].boxplot(df_rb["ff_points_total"].to_list(), notch=True)
    axs[0, 0].set_title('ff_points_total')
    axs[0, 0].grid()

    axs[0, 1].axis('off')  # Leeres Subplot für die zweite Spalte der ersten Zeile
    # Rushing 
    axs[1, 0].boxplot(df_rb["ff_points_rushing_yards"].to_list(), notch=True)
    axs[1, 0].set_title('ff Rushing Yards')
    axs[1, 0].grid()

    axs[1, 1].boxplot(df_rb["ff_points_rushing_tds"].to_list(), notch=True)
    axs[1, 1].set_title('ff Rushing TDs')
    axs[1, 1].grid()

    # Receiving
    axs[2, 0].boxplot(df_rb ["ff_points_receiving_yards"].to_list(), notch=True)
    axs[2, 0].set_title('ff Receiving Yards')
    axs[2, 0].grid()

    axs[2, 1].boxplot(df_rb["ff_points_receiving_tds"].to_list(), notch=True)
    axs[2, 1].set_title('ff Receiving TDs')
    axs[2, 1].grid()

    fig.suptitle(f"RB – Fantasy-Punkte bis Woche {week}")
    fig.tight_layout()
    fig.savefig(f"plots/rb/rb_ff_plots_week_{week}.png")