"""Erzeugt die Markdown-Dokumentation in `docs/` aus den Vorlagen in `doc_templates/`.

Die erzeugten Dateien sind normales Markdown mit Mermaid-Diagrammen. GitHub
zeigt sie direkt an, und MkDocs baut aus denselben Dateien die Website.

Aufruf im Projektordner:

    python tools/gen_docs.py           # Dateien in docs/ neu schreiben
    python tools/gen_docs.py --check   # nur prüfen, ob docs/ aktuell ist (CI)

In den Vorlagen werden zwei Anweisungen ersetzt:

- `--8<-- "datei:abschnitt"` fügt einen markierten Abschnitt einer Datei ein.
  Markiert wird er dort mit `<!-- --8<-- [start:abschnitt] -->` und
  `<!-- --8<-- [end:abschnitt] -->`. Ohne `:abschnitt` wird die ganze Datei
  eingefügt.
- `::: modul` erzeugt die API-Doku eines Moduls aus Docstrings und Type Hints.

Querverweise der Form ``[`text`][modul.Klasse.methode]`` werden zu Links auf
die passende Stelle der API-Doku.
"""

import argparse
import html
import logging
import os
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import quote

import griffe

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Quickstart mit Claude"
TEMPLATES = ROOT / "doc_templates"
OUT = ROOT / "docs"
REPO_BLOB = "https://github.com/Krysek/Quickstart-mit-Claude/blob/main/"

# Auf welcher Seite (relativ zu docs/) die API-Doku eines Moduls steht.
PAGES = {
    "model": "api/model.md",
    "menu": "api/menu.md",
    "animation": "api/animation.md",
    "view": "api/view.md",
    "Quickstart_mit_Claude": "api/app.md",
}

PARSER = griffe.Parser.google
SIGNATURE_WIDTH = 80

SNIPPET = re.compile(r'^--8<-- "([^"]+)"[ \t]*$', re.MULTILINE)
DIRECTIVE = re.compile(r"^::: ([\w.]+)[ \t]*$", re.MULTILINE)
CROSSREF = re.compile(r"\[([^\]]+)\]\[([\w.]+)\]")
MARKER = re.compile(r"--8<-- \[(start|end):[\w-]+\]")
# Codeblöcke, Querverweise mit Code-Label und Inline-Code, von links nach rechts gelesen.
CODE = re.compile(r"^```.*?^```|\[`[^`\n]+`\]\[[\w.]+\]|`[^`\n]+`", re.MULTILINE | re.DOTALL)


# --- Hilfsfunktionen -----------------------------------------------------


def anchor(path: str) -> str:
    """Bildet aus einem Pfad wie `model.Game.lock` die Sprungmarke `model-game-lock`.

    GitHub schreibt IDs klein, deshalb werden sie hier gleich klein erzeugt.
    """
    return path.lower().replace(".", "-")


def code_cell(text: str) -> str:
    """Formatiert Code für eine Tabellenzelle (`|` darf die Zelle nicht teilen)."""
    return "<code>" + html.escape(text).replace("|", "&#124;") + "</code>" if text else ""


def text_cell(text: str) -> str:
    """Formatiert Fließtext für eine Tabellenzelle (eine Zeile, `|` maskiert)."""
    return " ".join(text.split()).replace("|", "\\|")


def table(header: list[str], rows: list[list[str]]) -> str:
    """Baut eine Markdown-Tabelle."""
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join(lines)


def summary(obj: griffe.Object) -> str:
    """Erste Zeile des Docstrings (für Übersichtstabellen)."""
    return obj.docstring.value.split("\n", 1)[0] if obj.docstring else ""


def source_link(obj: griffe.Object) -> str:
    """Link auf die Stelle im Quelltext auf GitHub."""
    assert isinstance(obj.filepath, Path)
    rel = PurePosixPath(obj.filepath.resolve().relative_to(ROOT).as_posix())
    url = REPO_BLOB + quote(str(rel))
    if obj.lineno and not obj.is_module:
        url += f"#L{obj.lineno}-L{obj.endlineno or obj.lineno}"
    return f"[Quelltext: `{rel.name}`]({url})"


def documented_members(obj: griffe.Object) -> list[griffe.Object]:
    """Öffentliche, dokumentierte Mitglieder in Quelltext-Reihenfolge."""
    members = []
    for name, member in obj.members.items():
        if member.is_alias or name.startswith("_") or not member.docstring:
            continue
        assert isinstance(member, griffe.Object)
        members.append(member)
    return sorted(members, key=lambda m: m.lineno or 0)


def is_enum(cls: griffe.Class) -> bool:
    """True, wenn die Klasse von `Enum` erbt."""
    return any(str(base).split(".")[-1] == "Enum" for base in cls.bases)


def is_property(obj: griffe.Object) -> bool:
    """True für Eigenschaften (`@property`)."""
    return "property" in obj.labels


# --- Signaturen ------------------------------------------------------------


def format_params(params: list[griffe.Parameter]) -> list[str]:
    """Formatiert Parameter wie im Quelltext (ohne `self`)."""
    parts = []
    for p in params:
        if p.name in ("self", "cls"):
            continue
        prefix = {"var_positional": "*", "var_keyword": "**"}.get(p.kind.name if p.kind else "", "")
        text = prefix + p.name
        if p.annotation is not None:
            text += f": {p.annotation}"
        if p.default is not None:
            text += f" = {p.default}" if p.annotation is not None else f"={p.default}"
        parts.append(text)
    return parts


def signature(head: str, params: list[str], tail: str = "") -> str:
    """Setzt eine Signatur zusammen und bricht sie bei Überlänge pro Parameter um."""
    one_line = f"{head}({', '.join(params)}){tail}"
    if len(one_line) <= SIGNATURE_WIDTH or not params:
        return one_line
    inner = "".join(f"    {p},\n" for p in params)
    return f"{head}(\n{inner}){tail}"


def function_signature(func: griffe.Function) -> str:
    """Signatur einer Funktion oder Methode."""
    tail = f" -> {func.returns}" if func.returns is not None else ""
    return signature(f"def {func.name}", format_params(list(func.parameters)), tail)


def class_signature(cls: griffe.Class) -> str:
    """Signatur einer Klasse: Dekoratoren, Name und Parameter des Konstruktors."""
    decorators = "".join(f"@{d.value}\n" for d in cls.decorators)
    init = cls.all_members.get("__init__")
    if isinstance(init, griffe.Function) and not is_enum(cls):
        return decorators + signature(f"class {cls.name}", format_params(list(init.parameters)))
    bases = ", ".join(str(b) for b in cls.bases)
    return decorators + (f"class {cls.name}({bases})" if bases else f"class {cls.name}")


def code_block(code: str) -> str:
    """Python-Codeblock."""
    return f"```python\n{code}\n```"


# --- Docstrings ------------------------------------------------------------


def render_docstring(obj: griffe.Object, skip: tuple[str, ...] = ()) -> str:
    """Wandelt einen Google-Docstring in Markdown um (Text, Hinweise, Tabellen)."""
    if not obj.docstring:
        return ""
    blocks = []
    for section in obj.docstring.parse(PARSER):
        kind = section.kind.value
        if kind in skip:
            continue
        if kind == "text":
            blocks.append(section.value)
        elif kind == "admonition":
            title = section.title or section.value.annotation or ""
            body = section.value.description.splitlines()
            blocks.append("\n".join([f"> **{title}**", ">"] + [f"> {line}".rstrip() for line in body]))
        elif kind == "parameters":
            rows = [[f"`{p.name}`", code_cell(str(p.annotation or "")),
                     code_cell(str(p.default)) if p.default is not None else "erforderlich",
                     text_cell(p.description)] for p in section.value]
            blocks.append("**Parameter:**\n\n" + table(["Name", "Typ", "Standard", "Beschreibung"], rows))
        elif kind == "attributes":
            rows = [[f"`{a.name}`", code_cell(str(a.annotation or "")), text_cell(a.description)]
                    for a in section.value]
            blocks.append("**Attribute:**\n\n" + table(["Name", "Typ", "Beschreibung"], rows))
        elif kind in ("returns", "yields", "raises"):
            title = {"returns": "Rückgabe", "yields": "Liefert", "raises": "Löst aus"}[kind]
            rows = [[code_cell(str(r.annotation or "")), text_cell(r.description)] for r in section.value]
            blocks.append(f"**{title}:**\n\n" + table(["Typ", "Beschreibung"], rows))
        else:
            raise ValueError(f"{obj.path}: Docstring-Abschnitt '{kind}' wird nicht unterstützt")
    return "\n\n".join(blocks)


# --- API-Doku eines Moduls -----------------------------------------------------


def render_function(func: griffe.Function, level: int) -> str:
    """Abschnitt für eine Methode oder Funktion."""
    return "\n\n".join(filter(None, [
        f'<a id="{anchor(func.path)}"></a>',
        f"{'#' * level} `{func.name}()`",
        code_block(function_signature(func)),
        render_docstring(func),
        source_link(func),
    ]))


def render_property(attr: griffe.Attribute, level: int) -> str:
    """Abschnitt für eine Eigenschaft (`@property`)."""
    return "\n\n".join(filter(None, [
        f'<a id="{anchor(attr.path)}"></a>',
        f"{'#' * level} `{attr.name}` (Eigenschaft)",
        code_block(f"{attr.name}: {attr.annotation}"),
        render_docstring(attr),
        source_link(attr),
    ]))


def render_class(cls: griffe.Class, level: int) -> str:
    """Abschnitt für eine Klasse mit Konstruktor, Werten, Eigenschaften und Methoden."""
    parts = [
        f'<a id="{anchor(cls.path)}"></a>',
        f"{'#' * level} Klasse `{cls.name}`",
        code_block(class_signature(cls)),
        render_docstring(cls),
    ]
    init = cls.members.get("__init__")
    if isinstance(init, griffe.Function) and init.docstring:
        parts.append(render_docstring(init))
    if is_enum(cls):
        rows = [[f"`{m.name}`", text_cell(m.docstring.value if m.docstring else "")]
                for m in documented_members(cls)]
        parts.append("**Werte:**\n\n" + table(["Name", "Bedeutung"], rows))
    parts.append(source_link(cls))
    if not is_enum(cls):
        for member in documented_members(cls):
            if isinstance(member, griffe.Function):
                parts.append(render_function(member, level + 1))
            elif isinstance(member, griffe.Attribute) and is_property(member):
                parts.append(render_property(member, level + 1))
    return "\n\n".join(filter(None, parts))


def render_attribute(attr: griffe.Attribute, level: int) -> str:
    """Abschnitt für eine dokumentierte Modulvariable (z. B. einen Typ-Alias)."""
    annotation = f": {attr.annotation}" if attr.annotation is not None else ""
    return "\n\n".join(filter(None, [
        f'<a id="{anchor(attr.path)}"></a>',
        f"{'#' * level} `{attr.name}`",
        code_block(f"{attr.name}{annotation} = {attr.value}"),
        render_docstring(attr),
        source_link(attr),
    ]))


def kind_label(obj: griffe.Object) -> str:
    """Deutsche Bezeichnung der Art eines Objekts."""
    if isinstance(obj, griffe.Class):
        return "Aufzählung" if is_enum(obj) else "Klasse"
    if isinstance(obj, griffe.Function):
        return "Funktion"
    if isinstance(obj, griffe.Attribute) and str(obj.annotation) == "TypeAlias":
        return "Typ-Alias"
    return "Variable"


def render_module(module: griffe.Module) -> str:
    """Komplette API-Doku eines Moduls: Beschreibung, Übersicht, alle Mitglieder."""
    members = documented_members(module)
    rows = [[f"[`{m.name}`](#{anchor(m.path)})", kind_label(m), text_cell(summary(m))] for m in members]
    parts = [
        f'<a id="{anchor(module.path)}"></a>',
        f"## Modul `{module.name}`",
        render_docstring(module),
        source_link(module),
        "### Übersicht",
        table(["Name", "Art", "Beschreibung"], rows),
    ]
    for member in members:
        if isinstance(member, griffe.Class):
            parts.append(render_class(member, 3))
        elif isinstance(member, griffe.Function):
            parts.append(render_function(member, 3))
        elif isinstance(member, griffe.Attribute):
            parts.append(render_attribute(member, 3))
    return "\n\n".join(filter(None, parts))


def known_paths(module: griffe.Module) -> set[str]:
    """Alle Pfade, die in der API-Doku eine Sprungmarke bekommen."""
    paths = {module.path}
    for member in documented_members(module):
        paths.add(member.path)
        if isinstance(member, griffe.Class):
            paths.update(m.path for m in documented_members(member))
    return paths


# --- Vorlagen ----------------------------------------------------------------


def read_snippet(spec: str) -> str:
    """Liest `datei:abschnitt` (oder die ganze Datei) relativ zum Projektordner."""
    file, _, section = spec.partition(":")
    lines = (ROOT / file).read_text(encoding="utf-8").splitlines()
    if section:
        start = [i for i, line in enumerate(lines) if f"[start:{section}]" in line]
        end = [i for i, line in enumerate(lines) if f"[end:{section}]" in line]
        if len(start) != 1 or len(end) != 1 or start[0] > end[0]:
            raise ValueError(f"Abschnitt '{section}' in {file} nicht eindeutig gefunden")
        lines = lines[start[0] + 1:end[0]]
    return "\n".join(line for line in lines if not MARKER.search(line))


def link_crossrefs(text: str, page: str, targets: set[str]) -> str:
    """Ersetzt `[text][modul.pfad]` durch relative Links auf die API-Seiten."""
    def replace(match: re.Match[str]) -> str:
        label, path = match.groups()
        if path not in targets:
            raise ValueError(f"{page}: unbekannter Querverweis [{label}][{path}]")
        module = next(m for m in sorted(PAGES, key=len, reverse=True)
                      if path == m or path.startswith(m + "."))
        target_page = PAGES[module]
        rel = "" if target_page == page else os.path.relpath(
            target_page, os.path.dirname(page) or ".").replace(os.sep, "/")
        return f"[{label}]({rel}#{anchor(path)})"

    # Code (Blöcke und `...`, außer dem Label eines Querverweises) bleibt unverändert.
    hidden: list[str] = []

    def hide(match: re.Match[str]) -> str:
        if CROSSREF.fullmatch(match.group(0)):
            return match.group(0)
        hidden.append(match.group(0))
        return f"\0{len(hidden) - 1}\0"

    text = CODE.sub(hide, text)
    text = CROSSREF.sub(replace, text)
    return re.sub(r"\0(\d+)\0", lambda m: hidden[int(m.group(1))], text)


def generate() -> dict[Path, str]:
    """Erzeugt den Inhalt aller Dateien in docs/, die aus Vorlagen entstehen."""
    loader = griffe.GriffeLoader(search_paths=[str(SRC)], docstring_parser=PARSER)
    modules: dict[str, griffe.Module] = {}
    for name in PAGES:
        module = loader.load(name)
        assert isinstance(module, griffe.Module)
        modules[name] = module
    targets = set().union(*(known_paths(m) for m in modules.values()))

    result = {}
    for template in sorted(TEMPLATES.rglob("*.md")):
        page = template.relative_to(TEMPLATES).as_posix()
        text = template.read_text(encoding="utf-8")
        text = SNIPPET.sub(lambda m: read_snippet(m.group(1)), text)

        # page als Standardwert binden: die Funktion gehört zu genau dieser Vorlage.
        def module_doc(match: re.Match[str], page: str = page) -> str:
            module = modules.get(match.group(1))
            if module is None:
                raise ValueError(f"{page}: Modul '{match.group(1)}' fehlt in PAGES")
            return render_module(module)

        text = DIRECTIVE.sub(module_doc, text)
        text = link_crossrefs(text, page, targets)
        header = (f"<!-- Automatisch erzeugt aus doc_templates/{page} mit tools/gen_docs.py."
                  " Nicht von Hand bearbeiten. -->\n\n")
        result[OUT / page] = header + text.rstrip("\n") + "\n"
    return result


def main() -> int:
    """Schreibt oder prüft die erzeugten Dateien."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--check", action="store_true",
                        help="nichts schreiben, nur prüfen, ob docs/ aktuell ist")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    files = generate()
    outdated = [path for path, text in files.items()
                if not path.exists() or path.read_text(encoding="utf-8") != text]
    if args.check:
        for path in outdated:
            log.error("veraltet: %s", path.relative_to(ROOT).as_posix())
        if outdated:
            log.error("Bitte 'python tools/gen_docs.py' ausführen und die Änderungen "
                      "committen.")
            return 1
        log.info("docs/ ist aktuell (%d erzeugte Dateien).", len(files))
        return 0
    for path in outdated:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(files[path], encoding="utf-8", newline="\n")
        log.info("geschrieben: %s", path.relative_to(ROOT).as_posix())
    log.info("%d Dateien erzeugt, %d davon geändert.", len(files), len(outdated))
    return 0


if __name__ == "__main__":
    sys.exit(main())
