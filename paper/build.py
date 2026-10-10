"""Build the arXiv source and PDF of the paper from writeup/README.md.

    python paper/build.py           # writes paper/main.tex, paper/figures/, paper/main.pdf,
                                    # paper/arxiv_metadata.md and paper/arxiv-source.tar.gz

writeup/README.md stays the single source of the text, readable on GitHub. This script
converts it with pandoc, wraps it in a plain article preamble that arXiv's pdfLaTeX can
compile, copies the PDF figures beside it and runs pdflatex twice. Needs pandoc (3.x) and
a TeX distribution with pdflatex on PATH.

Conventions the script relies on in the Markdown source:
  * the first line is the title (`# ...`); the author comes from CITATION.cff;
  * text between `<!-- begin:github-only -->` and `<!-- end:github-only -->` is dropped;
  * `## Abstract` holds the abstract;
  * a figure is an image line followed by a caption line `*Figure N. ...*`;
  * a table caption is a line `*Table N. ...*` directly above the table;
  * section numbers are written in the headings, so LaTeX does not number them.
"""
from __future__ import annotations

import calendar
import gzip
import io
import os
import pathlib
import re
import shutil
import subprocess
import tarfile
import unicodedata

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "writeup" / "README.md"
OUT = ROOT / "paper"
FIGSRC = ROOT / "figures"

# characters pdfLaTeX's utf8 input does not cover on its own
UNICODE_MAP = {"ρ": r"\ensuremath{\rho}", "β": r"\ensuremath{\beta}", "−": r"\ensuremath{-}"}
# ASCII stand-ins for arXiv's metadata fields, which accept ASCII only
ASCII_MAP = {"ρ": "rho", "β": "beta", "−": "-", "×": "x", "÷": "/", "—": "--", "–": "-",
             "“": '"', "”": '"', "‘": "'", "’": "'"}

PREAMBLE = r"""\pdfoutput=1
\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[a4paper,margin=2.5cm]{geometry}
\usepackage{microtype}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{array,calc,booktabs,longtable}
\usepackage{etoolbox}
\usepackage[font=small,labelfont=bf]{caption}
\usepackage{newunicodechar}
\usepackage{xcolor}
\usepackage{xurl}
\usepackage[colorlinks=true,linkcolor=blue!50!black,urlcolor=blue!50!black,citecolor=blue!50!black]{hyperref}
\usepackage{bookmark}
%NEWUNICODECHARS%
\setcounter{secnumdepth}{0}  % section numbers are part of the headings
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\makeatletter
\def\maxwidth{\ifdim\Gin@nat@width>\linewidth\linewidth\else\Gin@nat@width\fi}
\def\maxheight{\ifdim\Gin@nat@height>0.6\textheight 0.6\textheight\else\Gin@nat@height\fi}
\def\fps@figure{htbp}
\makeatother
\setkeys{Gin}{width=\maxwidth,height=\maxheight,keepaspectratio}
\AtBeginEnvironment{longtable}{\small\setlength{\tabcolsep}{4pt}}
\setlength{\LTpre}{6pt}
\setlength{\LTpost}{6pt}
\setlength{\parskip}{4pt}
\setlength{\parindent}{0pt}
\hypersetup{pdftitle={%TITLE%},pdfauthor={%AUTHOR_PLAIN%}}
\title{%TITLE%}
\author{%AUTHOR%}
\date{}
\begin{document}
\maketitle
\begin{abstract}
%ABSTRACT%
\end{abstract}
"""


def _pandoc(md: str) -> str:
    cmd = ["pandoc", "-f", "markdown+pipe_tables+tex_math_dollars+implicit_figures-auto_identifiers",
           "-t", "latex", "--wrap=preserve", "--columns=10000", "--shift-heading-level-by=-1"]
    return subprocess.run(cmd, input=md, capture_output=True, text=True, check=True).stdout


def _author() -> str:
    cff = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    return r" \and ".join(f"{a['given-names']} {a['family-names']}" for a in cff["authors"])


def _split(md: str) -> tuple[str, str, str]:
    md = re.sub(r"<!-- begin:github-only -->.*?<!-- end:github-only -->\n?", "", md, flags=re.S)
    lines = md.splitlines()
    assert lines[0].startswith("# "), "first line must be the title"
    title = lines[0][2:].strip()
    body = "\n".join(lines[1:])
    m = re.search(r"^## Abstract\n(.*?)(?=^## )", body, flags=re.S | re.M)
    assert m, "no '## Abstract' section"
    abstract = m.group(1).strip()
    body = body[:m.start()] + body[m.end():]
    return title, abstract, body


def _figures(body: str) -> tuple[str, list[str]]:
    """Image + '*Figure N. caption*' -> captioned pandoc figure pointing at the PDF."""
    pat = re.compile(r"^!\[[^\]]*\]\(\.\./figures/(fig_[a-z0-9_]+)\.png\)\n\n\*Figure (\d+)\. (.+?)\*$", re.M)
    used, n_expected = [], 1
    def repl(m):
        nonlocal n_expected
        name, num, cap = m.group(1), int(m.group(2)), m.group(3)
        assert num == n_expected, f"figure {num} out of order (expected {n_expected})"
        n_expected += 1
        used.append(name)
        return f"![{cap}](figures/{name}.pdf)"
    body = pat.sub(repl, body)
    assert "../figures/" not in body, "a figure is missing its '*Figure N. ...*' caption line"
    return body, used


def _tables(body: str) -> str:
    """'*Table N. caption*' above a pipe table -> pandoc caption below it (LaTeX numbers it)."""
    pat = re.compile(r"^\*Table (A?\d+)\. (.+?)\*\n\n((?:\|.*\n)+)", re.M)
    body = body.rstrip("\n") + "\n"  # a table on the last line still needs its newline
    main_n = 1
    def repl(m):
        nonlocal main_n
        num, cap, table = m.group(1), m.group(2), m.group(3)
        if not num.startswith("A"):
            assert int(num) == main_n, f"table {num} out of order (expected {main_n})"
            main_n += 1
        return f"{table}\n: {cap}\n"
    body = pat.sub(repl, body)
    assert not re.search(r"^\*Table ", body, flags=re.M), "a table caption was not matched"
    return body


def _raw_latex(body: str) -> str:
    """Hanging-indent references; appendix tables numbered A1, A2, ..."""
    body = body.replace("## References\n", "## References\n\n```{=latex}\n\\begingroup\\small"
                        "\\setlength{\\parindent}{-1.5em}\\setlength{\\leftskip}{1.5em}"
                        "\\setlength{\\parskip}{3pt}\\everypar{}\n```\n", 1)  # everypar: indent the first entry too
    body = body.replace("## Appendix A.", "```{=latex}\n\\endgroup\n\\clearpage\n"
                        "\\setcounter{table}{0}\\renewcommand{\\thetable}{A\\arabic{table}}\n```\n\n"
                        "## Appendix A.", 1)
    return body


def _check_ascii(tex: str) -> None:
    left = sorted({ch for ch in tex if ord(ch) > 127 and ch not in UNICODE_MAP
                   and unicodedata.category(ch) not in ("Ll", "Lu")} - set("×÷–—“”‘’"))
    assert not left, f"characters with no LaTeX mapping: {left}"


def _ascii(text: str) -> str:
    for k, v in ASCII_MAP.items():
        text = text.replace(k, v)
    text = re.sub(r"\*\*?|`", "", text)  # Markdown emphasis and code marks
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    title, abstract, body = _split(SRC.read_text())
    body, figs = _figures(body)
    body = _raw_latex(_tables(body))

    tex_body = _pandoc(body)
    tex_abstract = _pandoc(abstract)
    unichars = "\n".join(f"\\newunicodechar{{{k}}}{{{v}}}" for k, v in UNICODE_MAP.items())
    tex = (PREAMBLE.replace("%NEWUNICODECHARS%", unichars).replace("%TITLE%", title)
           .replace("%AUTHOR%", _author()).replace("%AUTHOR_PLAIN%", _author().replace(r" \and ", ", ")).replace("%ABSTRACT%", tex_abstract.strip())
           + tex_body + "\n\\end{document}\n")
    _check_ascii(tex)

    figdir = OUT / "figures"
    if figdir.exists():
        shutil.rmtree(figdir)
    figdir.mkdir(parents=True)
    for name in figs:
        shutil.copy2(FIGSRC / f"{name}.pdf", figdir / f"{name}.pdf")
    (OUT / "main.tex").write_text(tex)

    # date the PDF by the price snapshot, so rebuilding unchanged inputs gives the same bytes
    retrieved = yaml.safe_load((ROOT / "config" / "prices.yaml").read_text())["_meta"]["retrieved_at"]
    epoch = calendar.timegm((int(retrieved[:4]), int(retrieved[5:7]), int(retrieved[8:10]), 0, 0, 0))
    env = {**os.environ, "SOURCE_DATE_EPOCH": str(epoch), "FORCE_SOURCE_DATE": "1"}
    for _ in range(2):  # second pass settles cross-references and the PDF outline
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                           cwd=OUT, capture_output=True, text=True, env=env)
        if r.returncode:
            print(r.stdout[-3000:])
            raise SystemExit("pdflatex failed; see paper/main.log")
    log = (OUT / "main.log").read_text(errors="replace")
    overfull = re.findall(r"^Overfull \\hbox \((\d+\.\d+)pt too wide\)", log, flags=re.M)
    big = [w for w in overfull if float(w) > 2.0]
    for ext in ("aux", "log", "out", "toc"):
        (OUT / f"main.{ext}").unlink(missing_ok=True)

    # arXiv takes the TeX source, not a TeX-made PDF: one upload with main.tex and figures/
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        for path in [OUT / "main.tex"] + sorted(figdir.glob("*.pdf")):
            info = tar.gettarinfo(str(path), arcname=str(path.relative_to(OUT)))
            info.mtime, info.uid, info.gid, info.uname, info.gname = 0, 0, 0, "", ""
            with open(path, "rb") as fh:
                tar.addfile(info, fh)
    (OUT / "arxiv-source.tar.gz").write_bytes(gzip.compress(buf.getvalue(), mtime=0))

    a_title, a_abstract = _ascii(title), _ascii(abstract)
    authors = _author().replace(r" \and ", ", ")
    assert len(a_abstract) <= 1920, f"abstract is {len(a_abstract)} characters; arXiv allows 1,920"
    (OUT / "arxiv_metadata.md").write_text(
        "# arXiv submission details\n\n"
        "Generated by `paper/build.py` from `writeup/README.md`. arXiv's metadata fields take "
        "ASCII only, so the text below has symbols spelled out.\n\n"
        f"## Title\n\n```\n{a_title}\n```\n\n"
        f"## Authors\n\n```\n{authors}\n```\n\n"
        f"## Abstract ({len(a_abstract)} of 1,920 characters)\n\n```\n{a_abstract}\n```\n\n"
        "## Files to upload\n\n"
        "`paper/arxiv-source.tar.gz` (it holds `main.tex` and `figures/`). arXiv compiles the "
        "source itself and usually refuses a PDF that was produced from TeX.\n\n"
        "## Suggested categories\n\n"
        "Primary `cs.CY` (Computers and Society), with cross-lists `cs.CL` (Computation and "
        "Language) and `econ.GN` (General Economics). `cs.CL` as primary is also defensible.\n\n"
        "## Licence\n\n"
        "Choose when submitting; the choice cannot be changed for that version. CC BY 4.0 "
        "matches the licence of the repository's data and figures.\n\n"
        "## Before submitting\n\n"
        "- The author list must name people only; AI use is disclosed in the paper's "
        "\"Use of AI assistance\" section.\n"
        "- A first submission to a category needs an endorsement from an established author "
        "in that category.\n"
        "- Tag the repository release cited in the paper (`v1.0.0`) before submitting.\n")
    print(f"wrote paper/main.tex, paper/main.pdf, {len(figs)} figures, paper/arxiv-source.tar.gz, "
          f"paper/arxiv_metadata.md (abstract {len(a_abstract)} chars)")
    if big:
        print(f"warning: {len(big)} overfull lines wider than 2pt: {big}")


if __name__ == "__main__":
    main()
