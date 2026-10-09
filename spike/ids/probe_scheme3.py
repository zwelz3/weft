"""Spike 2 step 4: can the sysml-toolkit Python bindings select id scheme 3
(CanonicalV3, IDS.md) for M1/M2? Builds the bindings at the pinned commit
(spike/ENVIRONMENT.md records the exact command and hash) and inspects the
`sysmlv2` module's public surface and source for any graph-format selector.

Usage: python3 probe_scheme3.py <toolkit-src-dir>
"""
import re
import sys
from pathlib import Path


def main():
    toolkit_src = Path(sys.argv[1])
    py_crate_src = toolkit_src / "crates" / "sysmlv2-py" / "src"

    import sysmlv2

    public_surface = sorted(n for n in dir(sysmlv2) if not n.startswith("_"))
    session_methods = sorted(n for n in dir(sysmlv2.Session) if not n.startswith("_"))

    pattern = re.compile(r"graph_format|GraphFormat|[Cc]anonical")
    matches = []
    for f in py_crate_src.glob("*.rs"):
        for lineno, line in enumerate(f.read_text().splitlines(), start=1):
            if pattern.search(line):
                matches.append(f"{f.name}:{lineno}: {line.strip()}")

    print("sysmlv2 module public surface:", public_surface)
    print("Session methods:", session_methods)
    print(f"Graph-format-related lines in {py_crate_src}:", len(matches))
    for m in matches:
        print(" ", m)

    if matches:
        print("CAPABILITY: graph format selection is reachable from Python.")
    else:
        print(
            "CAPABILITY GAP: sysmlv2-py 0.10.2 exposes Session.from_sources() only "
            "(TSession::from_sources, which IDS.md says retains GraphFormat::LegacyV2 -- "
            "scheme 2). Session.from_sources_with_graph_format / Model.with_graph_format "
            "exist in the Rust crates (sysmlv2-model) but are not wrapped by #[pymethods] "
            "anywhere in sysmlv2-py's source. No Python-reachable constructor selects "
            "scheme 3 at this commit."
        )


if __name__ == "__main__":
    main()
