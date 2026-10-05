# TetrisApp – Steuerung

[← Startseite der Dokumentation](../index.md)

Die `TetrisApp` hat keine eigene Spielschleife. Die Ereignisschleife von
tkinter ruft ihre Callbacks auf:

--8<-- "docs/architecture.md:ablauf"

## Spieltakt

--8<-- "docs/architecture.md:tick"

So arbeiten die Objekte zusammen, wenn ein Stein Reihen füllt:

--8<-- "docs/architecture.md:sequenz_loeschen"

## Tastatur

--8<-- "docs/architecture.md:tastatur"

--8<-- "docs/architecture.md:sequenz_taste"

::: Quickstart_mit_Claude
