# TetrisApp – Steuerung

[← Startseite der Dokumentation](../index.md)

Die `TetrisApp` hat keine eigene Spielschleife. Die Ereignisschleife von
tkinter ruft ihre Callbacks auf:

--8<-- "docs/architecture.md:ablauf"

## Spieltakt

--8<-- "docs/architecture.md:tick"

## Tastatur

--8<-- "docs/architecture.md:tastatur"

::: Quickstart_mit_Claude
