import polars as pl
import ff_functions as ff
from reportlab.platypus import Table, TableStyle, Image, PageBreak
from reportlab.lib.units import cm
from reportlab.lib import colors

def generate_defense_performance_table(week: int):
    def_stats = ff.get_def_stats()
    def_stats = def_stats.filter(pl.col("week") == week).sort(pl.col("ff_points_total"), descending=True)
    table_data = [
        ["Team", "Opp_Score", "Sacks \n (1)", "INTs \n (2)", "Fumbles \n (2)", "TDs \n (6)", "ff_points_total"]
    ]
    for i in range(10):
        row = def_stats[i]
        team = row["team"].item()
        opp_score = str(row["opp_score"].item()) + " (" + str(row["ff_points_opp_score"].item()) + ")"
        sacks = row["def_sacks"].item()
        ints = row["def_interceptions"].item()
        fumbles = row["fumble_recovery_opp"].item()
        tds = row["def_tds"].item()
        ff_total = row["ff_points_total"].item()
        table_data.append([team, opp_score, int(sacks), ints, fumbles, tds, ff_total])
    table = Table(
            table_data,
            colWidths=[2*cm, 2*cm, 2.2*cm, 2.5*cm, 2.5*cm],
            rowHeights=[1.2*cm] * len(table_data)
        )
    
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("VALIGN", (0,1), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"), # komplette Tabelle inkl. Kopfzeile zentrieren
    ]))
    return table