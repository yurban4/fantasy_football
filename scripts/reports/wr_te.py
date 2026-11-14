import polars as pl
import ff_functions as ff
from reportlab.platypus import Table, TableStyle, Image, PageBreak
from reportlab.lib.units import cm
from reportlab.lib import colors

def generate_wr_te_performance_table(week: int):
    wr_te_stats = ff.get_wr_te_stats()
    wr_te_stats = wr_te_stats.filter(pl.col("week") == week).sort(pl.col("ff_points_total"), descending=True)
    table_data = [
        ["WR/TE", "Team", "Receptions", "Rec Yards \n (%10)", "Rec TDs \n (6)", "ff_points_total"]
    ]
    for i in range(10):
        row = wr_te_stats[i]
        player = row["short_name"].item()
        team = row["team"].item()
        receptions = row["receptions"].item()
        rec_yards = row["receiving_yards"].item()
        rec_tds = row["receiving_tds"].item()
        ff_total = row["ff_points_total"].item()
        table_data.append([player, team, receptions, rec_yards, rec_tds, ff_total])
    table = Table(
            table_data,
            colWidths=[3*cm, 1.2*cm, 2.2*cm, 2.5*cm, 2.5*cm],
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