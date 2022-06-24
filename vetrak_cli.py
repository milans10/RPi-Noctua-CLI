import datetime
from time import sleep

from rich import box
from rich.align import Align
from rich.console import Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

MALINA = """[green]        
   .~~.   .~~.
  '. \ ' ' / .'[/][red]
   .~ .~~~..~.
  : .~.'~'.~. :
 ~ (   ) (   ) ~
( : '~'.~.'~' : )
 ~ .~ (   ) ~. ~
  (  : '~' :  ) 
   '~ .~~~. ~'
       '~'[/]
   [white]Raspberry Pi[/]
        """

CESTA = "/home/pi/skripty/mereni_data.db"  # cesta k databázi


class Nadpis:
    """
    Základní panel s nadpisem
    """

    def __rich__(self) -> Panel:
        text = Text("Raspberry Pi s automaticky řízeným větrákem Noctua a logování do SQLite", justify="center")
        text.stylize("green bold", 0, 10)
        text.stylize("red bold", 10, 13)
        text.stylize("white", 13, 65)
        text.stylize("white bold", 65)
        return Panel(text, style="turquoise2")


class Aktualne:
    """
    Panel s aktuálním měřením a datem
    """

    def __rich__(self) -> Panel:
        import os

        aktulni_cas = datetime.datetime.now().strftime("%A %d. %B %Y\n%H:%M:%S")
        cas = Text(str(aktulni_cas), justify="right", style="white bold")

        vystup_mereni = os.popen('vcgencmd measure_temp').readline()
        teplota_hodnota = (vystup_mereni.replace("temp=", "").replace("'C\n", ""))
        teplota_hodnota = str(int(round(float(teplota_hodnota), 0)))

        teplota = Text(str("\nAktuální teplota: " + teplota_hodnota + " °C"), justify="left", style="white")
        if float(teplota_hodnota) <= 50.0:
            teplota.stylize("green", 19)
        elif 50.0 < float(teplota_hodnota) < 65.0:
            teplota.stylize("dark_orange", 19)
        else:
            teplota.stylize("red", 19)

        autor = Text("\n\nvytvořil: Milan Švarc", justify="center")
        autor.stylize("white", 0, 11)
        autor.stylize("bright_yellow bold", 12)

        obsah = Group(cas, teplota, autor, Align.center(MALINA))

        return Panel(obsah, expand=True, style="turquoise2")


class Databaze:
    """
    Panel s daty z databáze
    """

    def __rich__(self) -> Panel:
        tabulka = Table(box=box.DOUBLE, expand=True, style="blue", title="[white bold]naměřené údaje[/]",
                        title_justify="center")
        tabulka.header_style = "white bold"
        tabulka.add_column("ČAS", justify="center")
        tabulka.add_column("TEPLOTA", justify="center")
        tabulka.add_column("NOCTUA", justify="center")

        df = pripoj_databazi(CESTA)

        for i in range(len(df) - 18, len(df)):
            tabulka.add_row(df.iloc[i, 0], str(df.iloc[i, 1]), df.iloc[i, 2])

        obsah = tabulka
        return Panel(obsah, style="turquoise2")


def muj_layout() -> Layout:
    """
    Základní layout

    :return: layout
    """
    layout = Layout()
    layout.split(
        Layout(name="nadpis", minimum_size=3, size=3),
        Layout(name="hlavni", minimum_size=25, size=25),
    )
    layout["hlavni"].split_row(
        Layout(name="aktualne", minimum_size=35),
        Layout(name="databaze", minimum_size=45),
    )
    return layout


def pripoj_databazi(soubor_db):
    """
    Připojí se k souboru s databází SQLite a vrátí Pandas.DateFrame s daty.
    :param soubor_db: cesta k souboru s databází
    :return: pandas.DateFrame
    """
    import sqlite3
    from sqlite3 import Error
    import pandas

    df = None
    try:
        conn = sqlite3.connect(soubor_db)
        try:
            df = pandas.read_sql_query("SELECT cas, teplota, noctua FROM noctua_rpi", conn)

        except Error as e:
            print(e)  # nelze načíst data

    except Error as e:
        print(e)  # nelzer vytvorit pripojeni k db

    return df


layout = muj_layout()
layout['nadpis'].update(Nadpis())
layout['aktualne'].update(Aktualne())
layout['databaze'].update(Databaze())

with Live(layout, refresh_per_second=2) as live:
    while True:
        sleep(0.1)
