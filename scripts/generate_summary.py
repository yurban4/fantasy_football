import polars as pl
import ff_functions as ff
import numpy as np
import nflreadpy as nfl
import matplotlib.pyplot as plt
from pathlib import Path
import os
import requests

from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer
from reportlab.platypus import Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

styles = getSampleStyleSheet()

toc = TableOfContents()
toc.levelStyles = [
    styles["Heading1"],
    styles["Heading2"],
    styles["Heading3"],
]


os.makedirs("reports", exist_ok=True)
os.makedirs("logos", exist_ok=True)


def download_image(url, filename="headshot.jpg"):
    r = requests.get(url)
    with open(filename, "wb") as f:
        f.write(r.content)
    return filename


def build_matchup_table(week: int):
    # Beispiel: deine Matchup-Daten
    df = (
        nfl.load_schedules(seasons=2026)
        .filter(pl.col("week") == week)
        .select([
            "home_team",
            "home_score",
            "away_team",
            "away_score",
            'result'
        ])
    )

    table_data = [
        ["Home Team", "", "Home Score", "Away Team", "", "Away Score"]
    ]

    for row in df.iter_rows(named=True):
        if row["result"] < 0:
            row_color = colors.lightgreen
        team_logo = Image(f"logos/{row['home_team']}.png", width=1.2*cm, height=1.2*cm)
        opp_logo = Image(f"logos/{row['away_team']}.png", width=1.2*cm, height=1.2*cm)
        styles = getSampleStyleSheet()
        body = styles["BodyText"]
        home = row["home_team"]
        home_score = row["home_score"]
        away = row["away_team"]
        away_score = row["away_score"]

        # Gewinner fett markieren
        if row["result"] > 0:
            home = Paragraph(f"<b>{home}</b>", body)
            home_score = Paragraph(f"<b>{home_score}</b>", body)
            away = Paragraph(away, body)
            away_score = Paragraph(f"{away_score}", body)
        elif row["result"] < 0:
            home = Paragraph(home, body)
            home_score = Paragraph(f"{home_score}", body)
            away = Paragraph(f"<b>{away}</b>", body)
            away_score = Paragraph(f"<b>{away_score}</b>", body)
        table_data.append([
        home,
        team_logo,
        home_score,
        away,
        opp_logo,
        away_score,
])

    table = Table(
        table_data,
        colWidths=[3*cm, 2*cm, 3*cm, 3*cm, 2*cm, 3*cm],
        rowHeights=[1.2*cm] * len(table_data)
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (2,1), (2,-1), "CENTER"),
        ("ALIGN", (5,1), (5,-1), "CENTER"),
    ]))

    return table

def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(
        doc.rightMargin,
        doc.bottomMargin - 10,
        f"{page_num}"
    )

#__________________________________________________________________________________________________
# Performance Report Functions
def generate_qb_performance_report(week: int):
    qb_stats = ff.get_qb_stats()
    qb_stats = qb_stats.filter(pl.col("week") == week)
    return qb_stats

def generate_kicker_performance_report(week: int):
    kick_stats = ff.get_kick_stats()
    kick_stats = kick_stats.filter(pl.col("week") == week).sort(pl.col("ff_points_total"), descending=True)
    print(kick_stats)
    table_data = [
        ["Kicker", "Team", "ff PAT (1)", "ff FG Short (3)", "ff FG Middle (4)", "ff FG Long (5)", "ff_points_total"]
    ]
    for i in range(10):
        row = kick_stats[i]
        kicker = row["short_name"].item()
        team = row["team"].item()
        ff_pat = row["ff_points_pat"].item()
        ff_short = row["ff_points_fg_0_39"].item()
        ff_middle = row["ff_points_fg_40_49"].item()
        ff_long = row["ff_points_fg_50_"].item()
        ff_total = row["ff_points_total"].item()
        table_data.append([kicker, team, ff_pat, ff_short, ff_middle, ff_long, ff_total])
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
#__________________________________________________________________________________________________

def generate_report(week: int):
    def add_toc_entry(self, flowable):
        if hasattr(flowable, "level") and hasattr(flowable, "_bookmarkName"):
            self.notify("TOCEntry", (flowable.level, flowable.getPlainText(), self.page))

    styles = getSampleStyleSheet()

    # 1. Dokument erzeugen
    doc = BaseDocTemplate(f"reports/week_{week}.pdf", pagesize=A4)
    doc.afterFlowable = add_toc_entry.__get__(doc)

    # 2. Frame definieren (Bereich, in dem Inhalt platziert wird)
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="normal"
    )
    doc.addPageTemplates([
        PageTemplate(id="normal", frames=[frame], onPage=add_page_number)
    ])

    story = []

    # --- TOC ---
    toc = TableOfContents()
    toc.levelStyles = [styles["Heading1"], styles["Heading2"]]

    # 5. Story beginnen
    story = []
    # Header
    # -----------------------------------------
    # 1) Deckblatt + TOC-Platzhalter
    # -----------------------------------------
    story.append(Paragraph(f"NFL Fantasy Report Week {week}", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Inhaltsverzeichnis", styles["Heading2"]))
    story.append(Spacer(1, 12))

    # Wir füllen das TOC später ein → Platzhalter
    toc_placeholder_index = len(story)
    story.append(Paragraph("TOC wird nach dem Build eingefügt …", styles["BodyText"]))

    story.append(PageBreak())

    # -----------------------------------------
    # 2) Kapitel sammeln (für TOC)
    # -----------------------------------------
    sections = []
    current_page = 2  # Seite 1 = Deckblatt/TOC

    # --- Kapitel 1 --- Match-Ups
    chapter_no = 1
    story.append(Paragraph(f"{chapter_no}. <b>Weekly Matchups</b>", styles["Heading2"]))
    sections.append((chapter_no, "Weekly Matchups", current_page))
    story.append(build_matchup_table(week))
    story.append(PageBreak())
    current_page += 1
    chapter_no += 1

    # --- Kapitel 2 --- QB 
    story.append(Paragraph(f"{chapter_no}. <b>QB Performance</b>", styles["Heading2"]))
    sections.append((chapter_no, "QB Performance", current_page))
    #story.append(generate_qb_performance_report(week))
    story.append(PageBreak())
    current_page += 1
    chapter_no += 1

    # --- Kapitel 3 --- RB 
    story.append(Paragraph(f"{chapter_no}. <b>RB Performance</b>", styles["Heading2"]))
    sections.append((chapter_no, "RB Performance", current_page))
    story.append(PageBreak())
    current_page += 1
    chapter_no += 1

    # --- Kapitel 4 --- WR/TE 
    story.append(Paragraph(f"{chapter_no}. <b>WR/TE Performance</b>", styles["Heading2"]))
    sections.append((chapter_no, "WR/TE Performance", current_page))
    story.append(PageBreak())
    current_page += 1
    chapter_no += 1

    # --- Kapitel 5 --- Kicker
    story.append(Paragraph(f"{chapter_no}. <b>Kicker Performance</b>", styles["Heading2"]))
    sections.append((chapter_no, "Kicker Performance", current_page))
    story.append(generate_kicker_performance_report(week))
    story.append(PageBreak())
    current_page += 1
    chapter_no += 1

    # --- Kapitel 6 --- Defense
    story.append(Paragraph(f"{chapter_no}. <b>Defense Performance</b>", styles["Heading2"]))
    sections.append((chapter_no, "Defense Performance", current_page))
    story.append(PageBreak())
    current_page += 1


    # -----------------------------------------
    # 3) TOC erzeugen (als Tabelle)
    # -----------------------------------------
    toc_data = [["Kapitel", "Name", "Seite"]]
    for chapter, title, page in sections:
        toc_data.append([f"{chapter}", title, str(page)])

    toc_table = Table(toc_data, colWidths=[3*cm, 12*cm, 2*cm])
    toc_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (1,1), (1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))

    # -----------------------------------------
    # 4) TOC an die richtige Stelle einfügen
    # -----------------------------------------
    story[toc_placeholder_index] = toc_table
    doc.afterFlowable = add_toc_entry.__get__(doc)
    doc.build(story)
    print(f"Report gespeichert unter: reports/week_{week}.pdf")


generate_report(week=5)