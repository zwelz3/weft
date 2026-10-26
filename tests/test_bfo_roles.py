"""Documentation must not say an information content entity bears a role.

BFO 2020 lets only an independent continuant bear a role. An information
content entity is a generically dependent continuant, so a software
component bears its component role through the material entity that
concretizes it (decision 0005). A sentence that has an information content
entity bear a role is checked for one of the markers that the sentence
states the concretization path or rejects the claim, in that sentence or
the next. The check reads only
the checkout (AGENTS.md rule 9).
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICE = re.compile(r"information content entit", re.IGNORECASE)
BEAR = re.compile(r"\b(bear|bears|bearing|borne|bearer)\b", re.IGNORECASE)
ROLE = re.compile(r"\brole\b", re.IGNORECASE)
ALLOWED = re.compile(r"concretiz|cannot|\bnot\b|rejected", re.IGNORECASE)
SENTENCE = re.compile(r"(?<=[.!?])\s+")


def documents():
    paths = [ROOT / "README.md", ROOT / "STATUS.md", ROOT / "AGENTS.md"]
    paths += sorted((ROOT / "docs").rglob("*.md"))
    return [p for p in paths if p.is_file() and "heal" not in p.relative_to(ROOT).parts]


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


def test_detector_accepts_the_concretization_path():
    text = "Information content entities whose concretizations bear the component role."
    assert not list(offending_sentences(text))


def test_no_document_has_an_ice_bear_a_role():
    found = []
    for path in documents():
        for sentence in offending_sentences(path.read_text(encoding="utf-8")):
            found.append(f"{path.relative_to(ROOT)}: {sentence}")
    assert not found, "\n".join(found)
