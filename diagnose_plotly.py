import importlib.util
import subprocess
import sys
import plotly.io as pio

def diagnose_plotly_kaleido():
    print("=== Plotly/Kaleido Diagnose ===")

    # 1) Prüfen: Ist Kaleido installiert?
    kaleido_installed = importlib.util.find_spec("kaleido") is not None
    print(f"Kaleido installiert: {kaleido_installed}")

    # 2) Prüfen: Plotly-Version
    try:
        import plotly
        print(f"Plotly-Version: {plotly.__version__}")
    except Exception as e:
        print(f"Plotly konnte nicht geladen werden: {e}")
        return

    # 3) Test: Kann Plotly ein Bild erzeugen?
    from plotly.express import line
    fig = line(x=[1,2,3], y=[1,4,9])

    try:
        pio.write_image(fig, "diagnose_test.png")
        print("Bildexport erfolgreich: Kaleido funktioniert.")
    except Exception as e:
        print("Bildexport fehlgeschlagen.")
        print(f"Fehler: {e}")

        # 4) Prüfen: Fehlende Linux-Libs (WSL)
        print("\nPrüfe Linux-Libraries...")
        libs = [
            "libgtk-3-0", "libx11-xcb1", "libxcb1", "libxcomposite1",
            "libxdamage1", "libxfixes3", "libxrandr2", "libxkbcommon0",
            "libpango-1.0-0", "libcairo2"
        ]

        missing_libs = []
        for lib in libs:
            result = subprocess.run(
                ["dpkg", "-s", lib],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode != 0:
                missing_libs.append(lib)

        if missing_libs:
            print("Fehlende Linux-Libs erkannt:")
            for lib in missing_libs:
                print(f"  - {lib}")
            print("\nInstalliere sie mit:")
            print("sudo apt-get install -y " + " ".join(missing_libs))
        else:
            print("Alle benötigten Linux-Libs vorhanden.")

        # 5) Chrome-Fallback erkennen
        if "Chrome" in str(e) or "chromium" in str(e).lower():
            print("\nPlotly fällt auf Chrome zurück → Kaleido wird nicht genutzt.")
            print("Ursachen:")
            print("- Kaleido nicht im richtigen venv")
            print("- Plotly-Version zu alt")
            print("- WSL-Libs fehlen")
            print("- Fehlerhafte Kaleido-Installation")

    print("\n=== Diagnose abgeschlossen ===")
