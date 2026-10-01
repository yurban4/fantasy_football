import datetime
from pathlib import Path

def df_to_markdown_table(df):
    """Convert Polars DataFrame to a Markdown table."""
    headers = " | ".join(df.columns)
    separator = " | ".join(["---"] * len(df.columns))
    rows = [" | ".join(map(str, row)) for row in df.iter_rows()]
    return "\n".join([headers, separator] + rows)


class MarkdownReport:
    def __init__(self, week: int, output_dir: str = "summaries"):
        self.week = week
        self.output_dir = Path(output_dir)
        self.lines = []

    def add_header(self):
        today = datetime.date.today().isoformat()
        self.lines.append(f"# Fantasy Football – Weekly Summary (Week {self.week})")
        self.lines.append(f"*Generated automatically on {today}*\n")

    def add_section(self, title: str):
        self.lines.append(f"## {title}\n")

    def add_text(self, text: str):
        self.lines.append(text + "\n")

    def add_table(self, df, title: str):
        self.add_section(title)
        self.lines.append(df_to_markdown_table(df) + "\n")

    def add_plot(self, plot_path: str, title: str):
        self.add_section(title)
        self.lines.append(f"![{title}]({plot_path})\n")

    def add_quote(self, text: str):
        self.lines.append(f"> {text}\n")

    def save(self):
        self.output_dir.mkdir(exist_ok=False)
        file_path = self.output_dir / f"week_{self.week}.md"
        file_path.write_text("\n".join(self.lines), encoding="utf-8")
        return file_path
