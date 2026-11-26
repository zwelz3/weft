"""Documentation must not say an information content entity bears a role.

BFO 2020 lets only an independent continuant bear a role. An information
content entity is a generically dependent continuant, so a software
component's role is borne by the material entity in which a concretization
of it inheres (decision 0005). A sentence that has an information content
entity bear a role is checked for one of the markers that the sentence
states the concretization path or rejects the claim, in that sentence or
the next. A second check applies to alignment axioms, which the decisions
state in table rows: a row that links
"is concretized by" (BFO_0000058) and "bearer of" (BFO_0000196) must also
link "inheres in" (BFO_0000197), because the range of the first and the
domain of the second are disjoint in BFO 2020. The checks read only the
checkout (AGENTS.md rule 9).
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICE = re.compile(r"information content entit", re.IGNORECASE)
BEAR = re.compile(r"\b(bear|bears|bearing|borne|bearer)\b", re.IGNORECASE)
ROLE = re.compile(r"\brole\b", re.IGNORECASE)
ALLOWED = re.compile(r"concretiz|cannot bear|does not bear|rejected", re.IGNORECASE)
SENTENCE = re.compile(r"(?<=[.!?])\s+")


def documents():
    paths = [ROOT / "README.md", ROOT / "STATUS.md", ROOT / "AGENTS.md"]
    paths += sorted((ROOT / "docs").rglob("*.md"))
    return [p for p in paths if p.is_file()]


def offending_sentences(text):
    for line in text.splitlines():
        sentences = SENTENCE.split(line)
        for i, sentence in enumerate(sentences):
            if ICE.search(sentence) and BEAR.search(sentence) and ROLE.search(sentence):
                following = sentences[i + 1] if i + 1 < len(sentences) else ""
                if not ALLOWED.search(sentence + " " + following):
                    yield sentence.strip()


def test_detector_flags_the_antipattern():
    claim = "Treat Component as a role borne by either a material artifact or an information content entity."
    assert list(offending_sentences(claim)) == [claim]


def test_detector_rejects_a_bare_negation():
    claim = "An information content entity bears the component role, not its carrier."
    assert list(offending_sentences(claim)) == [claim]


def test_detector_accepts_the_concretization_path():
    text = "Information content entities whose concretizations bear the component role."
    assert not list(offending_sentences(text))


def test_no_document_has_an_ice_bear_a_role():
    found = []
    for path in documents():
        for sentence in offending_sentences(path.read_text(encoding="utf-8")):
            found.append(f"{path.relative_to(ROOT)}: {sentence}")
    assert not found, "\n".join(found)


CONCRETIZED_BY = "BFO_0000058"
BEARER_OF = "BFO_0000196"
INHERES_IN = "BFO_0000197"


def test_concretization_axioms_route_through_inherence():
    found = []
    for path in documents():
        for line in path.read_text(encoding="utf-8").splitlines():
            # Axioms are stated in table rows; prose may name both relations to explain them.
            if line.startswith("|") and CONCRETIZED_BY in line and BEARER_OF in line and INHERES_IN not in line:
                found.append(f"{path.relative_to(ROOT)}: {line[:120]}")
    assert not found, "\n".join(found)
