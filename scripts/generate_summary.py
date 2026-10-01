import polars as pl
from markdown_renderer import MarkdownReport

def generate_summary(week: int):
    report = MarkdownReport(week)

    # Header
    report.add_header()

    # Overview (aus deiner Pipeline)
    overview_text = "Hohe Scoring-Woche mit starken RB-Leistungen und einigen Verletzungen."
    report.add_section("🏈 Weekly Overview")
    report.add_text(overview_text)

    # Top Performers
    top_qb = pl.DataFrame({
        "Player": ["Josh Allen", "Lamar Jackson"],
        "Team": ["BUF", "BAL"],
        "Points": [34.8, 31.2]
    })
    report.add_table(top_qb, "🔥 Top QBs")

    # Plots
    #report.add_plot("plots/week5_distribution.png", "📊 Points Distribution")

    # Save
    path = report.save()
    print(report)
    print(f"Saved report to {path}")

generate_summary(week=5)