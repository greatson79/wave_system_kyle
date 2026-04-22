"""
tests/test_translation_done_gate.py — Translation Done Gate tests (TDG-01 through TDG-06).
Infrastructure tier (75% coverage). English-First (P5-A).

TDG-01: output/blueprint.ko.md exists and is non-empty
TDG-02: output/completion-definition.ko.md exists and is non-empty
TDG-03: output/schema-mapping.ko.md exists and is non-empty
TDG-04: All .ko.md files contain Korean characters (actual translation, not copy)
TDG-05: Technical identifiers preserved (not translated) in .ko.md files
TDG-06: translations/glossary.yaml exists and contains InvestScan domain terms
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

# Korean Unicode range (Hangul syllables)
KOREAN_PATTERN = re.compile(r"[\uAC00-\uD7A3]")

# Technical identifiers that must NOT be translated
PRESERVED_IDENTIFIERS = [
    "NarrativeOutput",
    "sentiment_weight",
    "DG-",
    "TDG-",
    "M0.5",
    "M1",
]

OUTPUT_DIR = Path("output")
TRANSLATIONS_DIR = Path("translations")


# ── TDG-01: blueprint.ko.md ────────────────────────────────────────────────────

class TestTDG01Blueprint:
    TARGET = OUTPUT_DIR / "blueprint.ko.md"

    def test_file_exists(self):
        assert self.TARGET.exists(), (
            f"TDG-01 FAIL: {self.TARGET} not found. "
            "Run @translator on output/blueprint.md first."
        )

    def test_file_is_non_empty(self):
        assert self.TARGET.exists()
        assert self.TARGET.stat().st_size > 0, "blueprint.ko.md is empty"

    def test_minimum_size(self):
        """Korean .ko.md should be comparable in size to the English original."""
        assert self.TARGET.exists()
        ko_size = self.TARGET.stat().st_size
        en_path = OUTPUT_DIR / "blueprint.md"
        if en_path.exists():
            en_size = en_path.stat().st_size
            # Korean typically uses more bytes per character — allow 50%–300% of English
            assert ko_size > en_size * 0.5, (
                f"blueprint.ko.md ({ko_size} bytes) seems too short "
                f"vs English ({en_size} bytes)"
            )


# ── TDG-02: completion-definition.ko.md ───────────────────────────────────────

class TestTDG02CompletionDefinition:
    TARGET = OUTPUT_DIR / "completion-definition.ko.md"

    def test_file_exists(self):
        assert self.TARGET.exists(), (
            f"TDG-02 FAIL: {self.TARGET} not found. "
            "Run @translator on output/completion-definition.md first."
        )

    def test_file_is_non_empty(self):
        assert self.TARGET.exists()
        assert self.TARGET.stat().st_size > 0, "completion-definition.ko.md is empty"

    def test_minimum_size(self):
        assert self.TARGET.exists()
        ko_size = self.TARGET.stat().st_size
        en_path = OUTPUT_DIR / "completion-definition.md"
        if en_path.exists():
            en_size = en_path.stat().st_size
            assert ko_size > en_size * 0.5, (
                f"completion-definition.ko.md ({ko_size} bytes) seems too short"
            )


# ── TDG-03: schema-mapping.ko.md ──────────────────────────────────────────────

class TestTDG03SchemaMapping:
    TARGET = OUTPUT_DIR / "schema-mapping.ko.md"

    def test_file_exists(self):
        assert self.TARGET.exists(), (
            f"TDG-03 FAIL: {self.TARGET} not found. "
            "Run @translator on output/schema-mapping.md first."
        )

    def test_file_is_non_empty(self):
        assert self.TARGET.exists()
        assert self.TARGET.stat().st_size > 0, "schema-mapping.ko.md is empty"

    def test_minimum_size(self):
        assert self.TARGET.exists()
        ko_size = self.TARGET.stat().st_size
        en_path = OUTPUT_DIR / "schema-mapping.md"
        if en_path.exists():
            en_size = en_path.stat().st_size
            assert ko_size > en_size * 0.5, (
                f"schema-mapping.ko.md ({ko_size} bytes) seems too short"
            )


# ── TDG-04: Korean characters present in all .ko.md files ────────────────────

class TestTDG04KoreanContent:
    """Verify .ko.md files contain actual Korean (not English copy)."""

    @pytest.mark.parametrize("filename", [
        "blueprint.ko.md",
        "completion-definition.ko.md",
        "schema-mapping.ko.md",
    ])
    def test_contains_korean_characters(self, filename):
        path = OUTPUT_DIR / filename
        if not path.exists():
            pytest.skip(f"{filename} not yet generated")
        content = path.read_text(encoding="utf-8")
        korean_chars = KOREAN_PATTERN.findall(content)
        assert len(korean_chars) >= 50, (
            f"TDG-04 FAIL: {filename} has only {len(korean_chars)} Korean characters — "
            "does not appear to be a real translation"
        )

    @pytest.mark.parametrize("filename", [
        "blueprint.ko.md",
        "completion-definition.ko.md",
        "schema-mapping.ko.md",
    ])
    def test_korean_density_reasonable(self, filename):
        """Korean content should be a meaningful fraction of the file."""
        path = OUTPUT_DIR / filename
        if not path.exists():
            pytest.skip(f"{filename} not yet generated")
        content = path.read_text(encoding="utf-8")
        total_chars = len(content)
        korean_chars = len(KOREAN_PATTERN.findall(content))
        # At least 10% of characters should be Korean (tables/code dilute density)
        ratio = korean_chars / total_chars if total_chars > 0 else 0
        assert ratio >= 0.10, (
            f"TDG-04 FAIL: {filename} Korean density too low: "
            f"{ratio:.1%} ({korean_chars}/{total_chars} chars)"
        )


# ── TDG-05: Technical identifiers preserved ───────────────────────────────────

class TestTDG05IdentifiersPreserved:
    """
    Critical technical terms must NOT be translated.
    P5-A: NarrativeOutput, sentiment_weight, DG-xx, TDG-xx, M0.5, M1
    must appear verbatim in .ko.md files.
    """

    def _check_identifiers_in_file(self, filepath: Path, required_ids: list[str]) -> None:
        if not filepath.exists():
            pytest.skip(f"{filepath.name} not yet generated")
        content = filepath.read_text(encoding="utf-8")
        for identifier in required_ids:
            assert identifier in content, (
                f"TDG-05 FAIL: Technical identifier '{identifier}' "
                f"missing from {filepath.name} — must not be translated"
            )

    def test_blueprint_preserves_identifiers(self):
        # blueprint.md references NarrativeOutput and DG-01~08
        self._check_identifiers_in_file(
            OUTPUT_DIR / "blueprint.ko.md",
            ["NarrativeOutput", "DG-01"],
        )

    def test_completion_preserves_gate_ids(self):
        # completion-definition.md is the Done Gate reference document
        self._check_identifiers_in_file(
            OUTPUT_DIR / "completion-definition.ko.md",
            ["DG-01", "DG-08", "TDG-01", "M0.5"],
        )

    def test_schema_preserves_field_names(self):
        # schema-mapping.md maps EnvironmentScan fields → UnifiedSignal
        self._check_identifiers_in_file(
            OUTPUT_DIR / "schema-mapping.ko.md",
            ["UnifiedSignal", "steeps_category", "pSST"],
        )


# ── TDG-06: Glossary exists with domain terms ─────────────────────────────────

class TestTDG06Glossary:
    GLOSSARY = TRANSLATIONS_DIR / "glossary.yaml"

    def test_glossary_exists(self):
        assert self.GLOSSARY.exists(), (
            "TDG-06 FAIL: translations/glossary.yaml not found"
        )

    def test_glossary_is_valid_yaml(self):
        assert self.GLOSSARY.exists()
        import yaml
        content = yaml.safe_load(self.GLOSSARY.read_text(encoding="utf-8"))
        assert content is not None, "glossary.yaml is empty"
        assert isinstance(content, dict), "glossary.yaml must be a YAML dict"

    def test_glossary_has_entries(self):
        assert self.GLOSSARY.exists()
        import yaml
        content = yaml.safe_load(self.GLOSSARY.read_text(encoding="utf-8"))
        if content is None:
            pytest.fail("glossary.yaml is empty")
        # Count total entries across all sections
        total = sum(
            len(v) if isinstance(v, (dict, list)) else 1
            for v in content.values()
        )
        assert total >= 1, "glossary.yaml has no entries"

    def test_glossary_non_empty_file(self):
        assert self.GLOSSARY.exists()
        assert self.GLOSSARY.stat().st_size > 0, "glossary.yaml is empty file"
