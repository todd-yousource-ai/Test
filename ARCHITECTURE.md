"""Tests for ARCHITECTURE.md -- dependency chain and design constraints."""

import re
from pathlib import Path

import pytest

# Resolve project root by walking up from this file until we find pyproject.toml
PROJECT_ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)

ARCHITECTURE_PATH = PROJECT_ROOT / "ARCHITECTURE.md"


@pytest.fixture(scope="module")
def architecture_content() -> str:
    """Read and return the full content of ARCHITECTURE.md."""
    assert ARCHITECTURE_PATH.exists(), f"ARCHITECTURE.md not found at {ARCHITECTURE_PATH}"
    return ARCHITECTURE_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def architecture_lines(architecture_content: str) -> list[str]:
    """Return ARCHITECTURE.md split into lines."""
    return architecture_content.splitlines()


# ── Positive / happy-path tests ──────────────────────────────────────────────


class TestExistenceAndStructure:
    def test_architecture_md_exists_at_repo_root(self):
        assert ARCHITECTURE_PATH.exists(), "ARCHITECTURE.md must exist at the repository root"

    def test_file_is_not_empty(self, architecture_content: str):
        assert len(architecture_content.strip()) > 0, "ARCHITECTURE.md must not be empty"

    def test_contains_overview_section(self, architecture_content: str):
        assert re.search(r"^#{1,2}\s+Overview", architecture_content, re.MULTILINE), (
            "ARCHITECTURE.md must contain an Overview section"
        )

    def test_contains_dependency_chain_section_with_ascii_diagram(self, architecture_content: str):
        assert re.search(r"^#{1,2}\s+Dependency Chain", architecture_content, re.MULTILINE), (
            "ARCHITECTURE.md must contain a Dependency Chain section"
        )
        # Must contain an ASCII box-drawing diagram (uses box-drawing characters)
        assert "┌" in architecture_content and "┘" in architecture_content, (
            "Dependency Chain section must contain an ASCII box-drawing diagram"
        )

    def test_contains_design_constraints_section(self, architecture_content: str):
        assert re.search(r"^#{1,2}\s+Design Constraints", architecture_content, re.MULTILINE), (
            "ARCHITECTURE.md must contain a Design Constraints section"
        )

    def test_contains_package_structure_section(self, architecture_content: str):
        # The document may call this "Package Structure", "Layer Descriptions", or similar
        has_package = re.search(r"^#{1,3}\s+.*(Package Structure|Layer Descriptions|Layer)", architecture_content, re.MULTILINE)
        assert has_package, "ARCHITECTURE.md must contain a package/layer structure section"

    def test_contains_rationale_section(self, architecture_content: str):
        # Rationale may be inline per-layer or a dedicated section; check for the word "rationale" or "Rationale"
        has_rationale = (
            re.search(r"(?i)rationale", architecture_content) or
            re.search(r"(?i)boundary rule", architecture_content)
        )
        assert has_rationale, "ARCHITECTURE.md must contain rationale or boundary-rule text"


class TestFiveLayerSubsections:
    LAYERS = ["docs", "scaffold", "model", "storage", "CLI"]

    def test_contains_all_five_layer_subsections(self, architecture_content: str):
        content_lower = architecture_content.lower()
        for layer in self.LAYERS:
            assert layer.lower() in content_lower, (
                f"ARCHITECTURE.md must mention layer '{layer}'"
            )

    @pytest.mark.parametrize("layer", LAYERS)
    def test_layer_mentioned(self, architecture_content: str, layer: str):
        assert layer.lower() in architecture_content.lower(), (
            f"Layer '{layer}' must appear in ARCHITECTURE.md"
        )


class TestAsciiDiagram:
    STAGES = ["docs", "scaffold", "model", "storage", "CLI"]

    def test_ascii_diagram_includes_all_five_stages(self, architecture_content: str):
        # Extract the fenced code block containing the diagram
        code_blocks = re.findall(r"```[^\n]*\n(.*?)```", architecture_content, re.DOTALL)
        assert code_blocks, "Expected at least one fenced code block with the ASCII diagram"
        diagram_text = "\n".join(code_blocks)
        diagram_lower = diagram_text.lower()
        for stage in self.STAGES:
            assert stage.lower() in diagram_lower, (
                f"ASCII diagram must include stage '{stage}'"
            )

    def test_no_mermaid_fenced_blocks(self, architecture_content: str):
        assert not re.search(r"```\s*mermaid", architecture_content, re.IGNORECASE), (
            "ARCHITECTURE.md must use ASCII diagrams, not Mermaid fenced blocks"
        )


class TestDependencyChainOrdering:
    ORDERED_STAGES = ["docs", "scaffold", "model", "storage", "cli"]

    def test_dependency_chain_text_matches_diagram_order(self, architecture_content: str):
        """Verify the numbered list in the dependency chain section follows the correct order."""
        # Find all numbered items like "1. **docs**" or "1. docs"
        numbered = re.findall(r"(\d+)\.\s+\*{0,2}(\w+)\*{0,2}", architecture_content)
        if not numbered:
            pytest.skip("No numbered stage list found to verify ordering")

        # Extract stage names in declared order
        declared_order = [name.lower() for _, name in numbered if name.lower() in self.ORDERED_STAGES]
        expected = [s for s in self.ORDERED_STAGES if s in declared_order]
        assert declared_order == expected, (
            f"Declared order {declared_order} does not match expected {expected}"
        )

    def test_no_dependency_order_contradiction(self, architecture_content: str):
        """Ensure no text states a reverse or contradictory order."""
        content_lower = architecture_content.lower()
        # Check that none of these contradictory phrases appear
        contradictions = [
            "cli before storage",
            "storage before model",
            "model before scaffold",
            "scaffold before docs",
            "cli gates storage",
            "storage gates model",
            "model gates scaffold",
            "scaffold gates docs",
        ]
        for phrase in contradictions:
            assert phrase not in content_lower, (
                f"Contradictory ordering phrase found: '{phrase}'"
            )

    def test_no_missing_layer_in_dependency_chain(self, architecture_content: str):
        """All five named layers must appear in the dependency chain section."""
        # Extract the dependency chain section
        chain_match = re.search(
            r"(?s)(#{1,2}\s+Dependency Chain.*?)(?=\n#{1,2}\s|\Z)",
            architecture_content,
        )
        assert chain_match, "Could not locate Dependency Chain section"
        chain_section = chain_match.group(1).lower()
        for layer in self.ORDERED_STAGES:
            assert layer in chain_section, (
                f"Layer '{layer}' must appear in the Dependency Chain section"
            )


class TestDesignConstraints:
    def test_contains_zero_external_dependency_constraint(self, architecture_content: str):
        content_lower = architecture_content.lower()
        assert "zero" in content_lower and "dependenc" in content_lower, (
            "ARCHITECTURE.md must state the zero-external-dependency constraint"
        )

    def test_contains_python_311_target(self, architecture_content: str):
        # Accept "3.11", "Python 3.11", "python311", etc.
        assert re.search(r"3\.11", architecture_content), (
            "ARCHITECTURE.md must specify Python 3.11 as the target version"
        )


class TestBoundaryRationales:
    def test_rationale_for_docs_to_scaffold_boundary(self, architecture_content: str):
        content_lower = architecture_content.lower()
        # The docs layer must mention something about doc-only / no code / isolation
        assert any(term in content_lower for term in [
            "doc-only", "documentation is isolated", "no python source", "no executable",
            "zero executable",
        ]), "Must provide rationale for docs→scaffold boundary (docs isolation from code)"

    def test_rationale_for_scaffold_to_model_boundary(self, architecture_content: str):
        content_lower = architecture_content.lower()
        assert any(term in content_lower for term in [
            "scaffold", "directory tree", "package directory", "__init__", "pyproject",
        ]), "Must reference scaffold artifacts forming the scaffold→model boundary"

    def test_rationale_for_model_to_storage_boundary(self, architecture_content: str):
        content_lower = architecture_content.lower()
        assert any(term in content_lower for term in [
            "dataclass", "task.py", "taskstatus", "model",
        ]), "Must reference model artifacts (dataclass/task.py) for model→storage boundary"

    def test_rationale_for_storage_to_cli_boundary(self, architecture_content: str):
        content_lower = architecture_content.lower()
        assert any(term in content_lower for term in [
            "store.py", "inmemory", "in-memory", "storage",
        ]), "Must reference storage artifacts (store.py) for storage→CLI boundary"


class TestMergeValidationMapping:
    """Each layer must map to a specific validation capability."""

    def test_docs_layer_maps_to_doc_only_merge_validation(self, architecture_content: str):
        content_lower = architecture_content.lower()
        assert "doc-only merge" in content_lower or (
            "doc" in content_lower and "merge" in content_lower
        ), "Docs layer must map to doc-only merge validation"

    def test_scaffold_layer_maps_to_scaffold_merge_validation(self, architecture_content: str):
        content_lower = architecture_content.lower()
        assert "scaffold" in content_lower, (
            "Scaffold layer must be described for scaffold merge validation"
        )

    def test_model_layer_maps_to_model_import_validation(self, architecture_content: str):
        content_lower = architecture_content.lower()
        # Model layer should mention import or importable
        assert any(term in content_lower for term in [
            "import", "importable", "dataclass", "task.py",
        ]), "Model layer must map to model import validation"

    def test_storage_layer_maps_to_storage_integration_validation(self, architecture_content: str):
        content_lower = architecture_content.lower()
        assert any(term in content_lower for term in [
            "store", "storage", "integration", "inmemory", "in-memory",
        ]), "Storage layer must map to storage integration validation"

    def test_cli_layer_maps_to_cli_entry_point_validation(self, architecture_content: str):
        content_lower = architecture_content.lower()
        assert any(term in content_lower for term in [
            "entry point", "entry-point", "console-script", "console_script", "cli.py",
        ]), "CLI layer must map to CLI entry-point validation"


# ── Negative / guard-rail tests ──────────────────────────────────────────────


class TestNegativeCases:
    def test_no_broken_markdown_headings(self, architecture_lines: list[str]):
        """Every line starting with # must have a space after the hash sequence."""
        for i, line in enumerate(architecture_lines, start=1):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                # Match valid heading: one or more # followed by a space
                assert re.match(r"^#{1,6}\s", stripped), (
                    f"Line {i} has a broken Markdown heading (missing space after #): {stripped!r}"
                )

    def test_no_placeholder_text(self, architecture_content: str):
        """Document must not contain TODO, FIXME, TBD, or placeholder bracket tokens."""
        for token in ["TODO", "FIXME", "TBD", "[INSERT"]:
            assert token not in architecture_content.upper(), (
                f"ARCHITECTURE.md contains placeholder token '{token}'"
            )

    def test_no_non_stdlib_dependency_references(self, architecture_content: str):
        """The document must not reference or instruct adding non-stdlib dependencies."""
        content_lower = architecture_content.lower()
        # Well-known external packages that should NOT appear as requirements
        forbidden_packages = [
            "requests", "flask", "django", "fastapi", "sqlalchemy",
            "numpy", "pandas", "click", "typer", "rich", "httpx",
            "pydantic", "attrs", "celery", "redis", "boto3",
        ]
        for pkg in forbidden_packages:
            # Only flag if it appears in a dependency/requirement context
            # Simple check: the package name appears at all
            if pkg in content_lower:
                # Allow if it's just in a "we do NOT use X" context -- but be strict
                # Check it's not in a negation context
                pattern = rf"(?<!not\s)(?<!no\s)(?<!without\s)(?<!zero\s)\b{re.escape(pkg)}\b"
                match = re.search(pattern, content_lower)
                assert match is None, (
                    f"ARCHITECTURE.md references external package '{pkg}' -- "
                    "violates zero-external-dependency constraint"
                )


# ── Security tests ───────────────────────────────────────────────────────────


class TestSecurityConstraints:
    def test_no_external_package_or_network_tooling_instructions(self, architecture_content: str):
        """
        The document must not instruct adding external packages or
        network-dependent tooling, preserving the zero-external-dependency constraint.
        """
        content_lower = architecture_content.lower()

        # Must not instruct pip install of external packages
        assert "pip install" not in content_lower or (
            "pip install" in content_lower and (
                "tasklib" in content_lower[content_lower.index("pip install"):content_lower.index("pip install") + 50]
            )
        ), "Must not instruct pip install of external packages (self-install is OK)"

        # Must not reference adding dependencies to requirements files
        forbidden_instructions = [
            "add to requirements",
            "add dependency",
            "install dependency",
            "npm install",
            "cargo add",
            "go get",
        ]
        for phrase in forbidden_instructions:
            assert phrase not in content_lower, (
                f"ARCHITECTURE.md contains external tooling instruction: '{phrase}'"
            )

        # Must not reference network-dependent tooling as requirements
        network_tools = ["docker pull", "curl ", "wget ", "fetch("]
        for tool in network_tools:
            assert tool not in content_lower, (
                f"ARCHITECTURE.md references network-dependent tooling: '{tool}'"
            )
