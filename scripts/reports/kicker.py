import polars as pl
import ff_functions as ff
from reportlab.platypus import Table, TableStyle, Image, PageBreak
from reportlab.lib.units import cm
from reportlab.lib import colors

def generate_kicker_performance_table(week: int):
    kick_stats = ff.get_kick_stats()
    kick_stats = kick_stats.filter(pl.col("week") == week).sort(pl.col("ff_points_total"), descending=True)
    table_data = [
        ["Kicker", "Team", "PAT \n (1)", "FG Short \n (3)", "FG Middle \n (4)", "FG Long \n (5)", "ff_points_total"]
    ]
    for i in range(10):
        row = kick_stats[i]
        kicker = row["short_name"].item()
        team = row["team"].item()
        pat = row["pat_made"].item()
        pat_missed = row["pat_missed"].item()
        fg_short = row["fg_made_0_19"].item() + row["fg_made_20_29"].item() + row["fg_made_30_39"].item()
        fg_short_missed = row["fg_missed_0_19"].item() + row["fg_missed_20_29"].item() + row["fg_missed_30_39"].item()
        fg_middle = row["fg_made_40_49"].item()
        fg_middle_missed = row["fg_missed_40_49"].item()
        fg_long = row["fg_made_50_59"].item() + row["fg_made_60_"].item()
        fg_long_missed = row["fg_missed_50_59"].item() + row["fg_missed_60_"].item()
        ff_total = row["ff_points_total"].item()
        table_data.append([kicker, team,
                            str(pat) + "/" + str(pat_missed), 
                           str(fg_short) + "/" + str(fg_short_missed), 
                           str(fg_middle) + "/" + str(fg_middle_missed), 
                           str(fg_long) + "/" + str(fg_long_missed), 
                           str(ff_total)])
    table = Table(
            table_data,
            colWidths=[3*cm, 1.5*cm, 2.5*cm, 3*cm, 3*cm, 2.5*cm, 3*cm],
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