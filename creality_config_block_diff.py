#!/usr/bin/env python3
import sys, os, html

MARKER = "; CONFIG_BLOCK_START"
TEMPLATE = os.path.join(os.path.dirname(__file__), "diff_template.html")


def parse(path):
    config, active = {}, False
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not active:
            active = line == MARKER
            continue
        if not line.startswith(";"):
            continue
        content = line[1:].strip()
        key, _, val = content.partition("=")
        config[key.strip()] = val.strip()
    return config


def render(a, b, ca, cb):
    rows = []
    for key in sorted(set(ca) | set(cb)):
        va, vb = ca.get(key), cb.get(key)
        if va == vb:
            continue
        cls = "missing" if None in (va, vb) else "diff"
        ea = html.escape(va) if va is not None else "<em>missing</em>"
        eb = html.escape(vb) if vb is not None else "<em>missing</em>"
        rows.append(f'<tr class="{cls}"><td class="k">{html.escape(key)}</td><td>{ea}</td><td>{eb}</td></tr>')

    ba, bb = html.escape(os.path.basename(a)), html.escape(os.path.basename(b))
    table = (
        f'<table><thead><tr><th>Key</th><th title="{html.escape(a)}">{ba}</th><th title="{html.escape(b)}">{bb}</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
        if rows else "<p>No differences found.</p>"
    )

    return (
        open(TEMPLATE, encoding="utf-8").read()
        .replace("{file_a}", html.escape(a))
        .replace("{file_b}", html.escape(b))
        .replace("{table}", table)
    )


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <file_a> <file_b>", file=sys.stderr)
    sys.exit(1)

a, b = sys.argv[1], sys.argv[2]
out = "diff_output.html"
open(out, "w", encoding="utf-8").write(render(a, b, parse(a), parse(b)))
print(f"Written: {out}")
os.system(f"open {out!r}")
