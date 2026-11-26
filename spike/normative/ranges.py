"""Build a (metaclass, property) -> declared range map from the toolkit's
published KerML/SysML JSON Schema at the pinned commit. The schema's $ref
$comment on each array-item or oneOf branch names the metaclass the toolkit
declares as that property's range; convert.py uses this map to decide every
object property's range before emitting it (AGENTS.md rule 5), rather than
guessing from observed data.
"""
import json
import os
from pathlib import Path

# The schema files live in a sysml-toolkit source checkout at the commit
# decision 0002 pins. The checkout's location is given by the environment
# variable SYSMLV2_TOOLKIT_SRC, so no machine-specific path is built in.
TOOLKIT_SRC_ENV = "SYSMLV2_TOOLKIT_SRC"


def schema_path(name):
    """Path to `spec-refs/<name>` in the toolkit checkout named by
    SYSMLV2_TOOLKIT_SRC."""
    root = os.environ.get(TOOLKIT_SRC_ENV)
    if not root:
        raise SystemExit(
            f"{TOOLKIT_SRC_ENV} is not set; point it at a sysml-toolkit source "
            "checkout at the commit decision 0002 pins"
        )
    return Path(root) / "spec-refs" / name


def schema_files():
    return [schema_path("KerML.schema.json"), schema_path("SysML.schema.json")]


def _range_from_node(node):
    if not isinstance(node, dict):
        return None
    comment = node.get("$comment")
    if comment:
        return comment.rsplit("/", 1)[-1]
    for key in ("oneOf", "anyOf"):
        for branch in node.get(key, []):
            r = _range_from_node(branch)
            if r:
                return r
    items = node.get("items")
    if items:
        return _range_from_node(items)
    return None


def build_range_map():
    """Returns {(metaclass, property): range_metaclass}, plus a
    property-name-only fallback map for properties whose range does not vary
    by owning metaclass."""
    per_class = {}
    by_name = {}
    for path in schema_files():
        defs = json.load(open(path, encoding="utf-8"))["$defs"]
        for cls, schema in defs.items():
            variants = schema.get("anyOf") or [schema]
            for variant in variants:
                props = variant.get("properties", {})
                for prop, node in props.items():
                    r = _range_from_node(node)
                    if r is None:
                        continue
                    per_class[(cls, prop)] = r
                    by_name.setdefault(prop, set()).add(r)
    return per_class, by_name


if __name__ == "__main__":
    per_class, by_name = build_range_map()
    print(f"{len(per_class)} (metaclass, property) ranges from schema")
    multi = {k: v for k, v in by_name.items() if len(v) > 1}
    print(f"{len(multi)} properties whose range varies by owning metaclass")
