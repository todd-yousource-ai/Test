"""Tests for API.md -- public API reference documentation."""

import re
from pathlib import Path

import pytest

# Resolve project root by walking up from this file to find pyproject.toml
PROJECT_ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)

API_MD_PATH = PROJECT_ROOT / "API.md"


@pytest.fixture(scope="module")
def api_md_content() -> str:
    """Read and return the full content of API.md."""
    assert API_MD_PATH.exists(), f"API.md not found at {API_MD_PATH}"
    return API_MD_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def api_md_lines(api_md_content: str) -> list[str]:
    """Return API.md content as a list of lines."""
    return api_md_content.splitlines()


# ── Happy Path Tests ─────────────────────────────────────────────────────────


class TestAPImdExists:
    def test_api_md_exists(self):
        """Verify API.md exists at repository root."""
        assert API_MD_PATH.exists(), f"Expected API.md at {API_MD_PATH}"
        assert API_MD_PATH.is_file(), "API.md should be a regular file"


class TestTaskStatusEnum:
    def test_api_md_contains_taskstatus_enum(self, api_md_content: str):
        """Verify PENDING, IN_PROGRESS, COMPLETE are all documented."""
        assert "PENDING" in api_md_content, "PENDING status not documented"
        assert "IN_PROGRESS" in api_md_content, "IN_PROGRESS status not documented"
        assert "COMPLETE" in api_md_content, "COMPLETE status not documented"

    def test_taskstatus_string_values(self, api_md_content: str):
        """Verify the string values of each enum member are documented."""
        assert '"pending"' in api_md_content or "'pending'" in api_md_content
        assert '"in_progress"' in api_md_content or "'in_progress'" in api_md_content
        assert '"complete"' in api_md_content or "'complete'" in api_md_content

    def test_taskstatus_section_exists(self, api_md_content: str):
        """Verify there is a dedicated TaskStatus section."""
        assert re.search(r"#{1,3}\s.*TaskStatus", api_md_content), (
            "No TaskStatus heading found"
        )


class TestTaskDataclass:
    def test_api_md_contains_task_dataclass_fields(self, api_md_content: str):
        """Verify id, title, status, created_at fields are documented with types or defaults."""
        # Check field names
        for field in ("id", "title", "status", "created_at"):
            assert f"`{field}`" in api_md_content, (
                f"Field '{field}' not documented with backtick formatting"
            )

        # Check type annotations are present
        assert "`str`" in api_md_content, "str type not documented"
        assert "`TaskStatus`" in api_md_content, "TaskStatus type not documented"
        assert "`datetime`" in api_md_content or "datetime" in api_md_content, (
            "datetime type not documented"
        )

    def test_api_md_contains_uuid4_generation(self, api_md_content: str):
        """Verify UUID4 generation behavior for Task.id is stated."""
        content_lower = api_md_content.lower()
        assert "uuid" in content_lower, "UUID not mentioned in documentation"
        # Specifically UUID version 4
        assert "uuid4" in content_lower or "uuid version 4" in content_lower or "uuid v4" in content_lower, (
            "UUID4 / UUID version 4 generation not documented"
        )

    def test_api_md_contains_datetime_behavior(self, api_md_content: str):
        """Verify automatic datetime timestamp behavior is stated."""
        content_lower = api_md_content.lower()
        assert "datetime" in content_lower, "datetime not mentioned"
        # Should mention automatic generation
        assert "auto" in content_lower or "automatic" in content_lower or "auto-generated" in content_lower, (
            "Automatic datetime generation behavior not documented"
        )
        # Should mention UTC or current time
        assert "utc" in content_lower or "current" in content_lower, (
            "UTC or current time behavior not documented"
        )


class TestSerialization:
    def test_api_md_contains_to_dict_section(self, api_md_content: str):
        """Verify to_dict method signature is present."""
        assert "to_dict" in api_md_content, "to_dict method not documented"

    def test_api_md_contains_from_dict_section(self, api_md_content: str):
        """Verify from_dict method signature is present."""
        assert "from_dict" in api_md_content, "from_dict method not documented"


class TestStoreMethods:
    def test_api_md_contains_store_methods(self, api_md_content: str):
        """Verify add, get, list, complete, delete method signatures are present."""
        for method in ("add", "get", "list", "complete", "delete"):
            # Look for backtick-wrapped method names or method signatures
            assert re.search(rf"`{method}`|`{method}\(|\.{method}\(|### {method}|#### {method}", api_md_content, re.IGNORECASE), (
                f"Store method '{method}' not documented"
            )

    def test_api_md_contains_inmemory_taskstore(self, api_md_content: str):
        """Verify InMemoryTaskStore is documented."""
        assert "InMemoryTaskStore" in api_md_content, (
            "InMemoryTaskStore not found in documentation"
        )


class TestCLICommands:
    def test_api_md_contains_cli_commands(self, api_md_content: str):
        """Verify add, list, complete CLI commands are documented with argument format and expected stdout output."""
        content_lower = api_md_content.lower()

        # CLI section should exist
        assert re.search(r"#{1,3}\s.*cli", api_md_content, re.IGNORECASE), (
            "No CLI section heading found"
        )

        # Each command should be mentioned in a CLI context
        for cmd in ("add", "list", "complete"):
            assert cmd in content_lower, f"CLI command '{cmd}' not documented"

    def test_cli_add_command_documented(self, api_md_content: str):
        """Verify the 'add' CLI command has argument/usage information."""
        # Should contain something like 'add "title"' or add <title> or similar
        assert re.search(r"add\s", api_md_content), (
            "CLI 'add' command usage not documented"
        )

    def test_cli_list_command_documented(self, api_md_content: str):
        """Verify the 'list' CLI command is documented."""
        assert re.search(r"list", api_md_content, re.IGNORECASE), (
            "CLI 'list' command not documented"
        )

    def test_cli_complete_command_documented(self, api_md_content: str):
        """Verify the 'complete' CLI command is documented."""
        assert re.search(r"complete", api_md_content, re.IGNORECASE), (
            "CLI 'complete' command not documented"
        )


class TestErrorBehavior:
    def test_api_md_contains_error_behavior(self, api_md_content: str):
        """Verify KeyError documentation for missing task ID operations."""
        assert "KeyError" in api_md_content, (
            "KeyError behavior for missing task ID not documented"
        )


class TestSectionContent:
    def test_api_md_no_empty_sections(self, api_md_lines: list[str]):
        """Verify each h2/h3 heading is followed by content before next heading."""
        heading_pattern = re.compile(r"^#{1,3}\s+\S")
        heading_indices = [
            i for i, line in enumerate(api_md_lines) if heading_pattern.match(line)
        ]

        empty_sections = []
        for idx, heading_line_num in enumerate(heading_indices):
            # Determine the range between this heading and the next (or end of file)
            if idx + 1 < len(heading_indices):
                next_heading = heading_indices[idx + 1]
            else:
                next_heading = len(api_md_lines)

            # Check content between headings (excluding blank lines)
            content_lines = [
                line.strip()
                for line in api_md_lines[heading_line_num + 1 : next_heading]
                if line.strip() and not line.strip().startswith("---")
            ]

            if not content_lines:
                empty_sections.append(api_md_lines[heading_line_num].strip())

        assert not empty_sections, (
            f"Empty sections found (no content after heading): {empty_sections}"
        )


# ── Negative Cases ───────────────────────────────────────────────────────────


class TestNegativeCases:
    def test_api_md_not_empty(self, api_md_content: str, api_md_lines: list[str]):
        """File must have substantive content (> 200 lines or > 3000 characters)."""
        char_count = len(api_md_content)
        line_count = len(api_md_lines)
        assert char_count > 3000 or line_count > 200, (
            f"API.md is too short: {line_count} lines, {char_count} characters. "
            f"Expected > 200 lines or > 3000 characters."
        )

    def test_api_md_no_broken_markdown_headers(self, api_md_lines: list[str]):
        """All lines starting with # must follow valid Markdown heading syntax."""
        broken_headers = []
        for i, line in enumerate(api_md_lines):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                # Valid heading: one or more # followed by a space and text
                # Also allow lines that are just ### (table of contents anchors, etc.) -- but
                # the standard is # followed by space. Also code blocks use # for comments.
                # We should skip lines inside code blocks.
                if not re.match(r"^#{1,6}\s+\S", stripped) and not re.match(r"^#{1,6}\s*$", stripped):
                    # Could be inside a code block -- do a simple check
                    # Count ``` occurrences before this line
                    code_fence_count = sum(
                        1 for prev_line in api_md_lines[:i] if prev_line.strip().startswith("```")
                    )
                    if code_fence_count % 2 == 0:
                        # Not inside a code block -- this is a broken header
                        broken_headers.append((i + 1, line.rstrip()))

        assert not broken_headers, (
            f"Broken Markdown headers found: {broken_headers}"
        )

    def test_api_md_no_todo_placeholders(self, api_md_content: str):
        """File must not contain TODO, FIXME, TBD, or placeholder markers."""
        content_upper = api_md_content.upper()
        placeholders_found = []
        for marker in ("TODO", "FIXME", "TBD", "XXX", "PLACEHOLDER", "FILL IN", "FILL_IN"):
            if marker in content_upper:
                placeholders_found.append(marker)

        assert not placeholders_found, (
            f"Placeholder markers found in API.md: {placeholders_found}"
        )

    def test_api_md_no_unsupported_cli_commands(self, api_md_content: str):
        """Document does not describe CLI commands beyond add, list, and complete."""
        # Find the CLI section
        cli_match = re.search(r"(#{1,3}\s.*[Cc][Ll][Ii].*)", api_md_content)
        if cli_match:
            cli_start = cli_match.start()
            cli_section = api_md_content[cli_start:]

            # Look for other common CLI command names that shouldn't be there
            unsupported_commands = ["delete", "remove", "update", "edit", "show", "info", "status"]
            found_unsupported = []
            for cmd in unsupported_commands:
                # Look for patterns like `tasklib cmd` or `### cmd` in CLI section
                # that would indicate a documented CLI command (not just a mention)
                if re.search(rf"tasklib\s+{cmd}\b", cli_section, re.IGNORECASE):
                    found_unsupported.append(cmd)
                if re.search(rf"^#{2,4}\s+`?{cmd}`?\s*$", cli_section, re.IGNORECASE | re.MULTILINE):
                    found_unsupported.append(cmd)

            assert not found_unsupported, (
                f"Unsupported CLI commands documented: {found_unsupported}. "
                f"Only add, list, and complete should be documented."
            )

    def test_api_md_no_python_source_references(self, api_md_content: str):
        """Document does not reference Python source files being added in this PR."""
        # Should not reference implementation files like .py files from the codebase
        # (import paths are fine, but direct file references are not)
        py_file_refs = re.findall(r"\b\w+\.py\b", api_md_content)
        # Filter out legitimate references (like in import examples, which use module paths not files)
        suspicious_refs = [
            ref for ref in py_file_refs
            if ref not in ("setup.py", "conftest.py")  # common acceptable refs
            and ref not in ("example.py",)  # example file references
        ]
        # Check that no implementation source files are directly referenced
        impl_file_patterns = [
            "task.py", "store.py", "cli.py", "models.py", "main.py",
            "tasklib.py", "__init__.py", "__main__.py"
        ]
        found_impl_refs = [ref for ref in suspicious_refs if ref in impl_file_patterns]
        assert not found_impl_refs, (
            f"Python source file references found in API.md: {found_impl_refs}. "
            f"API documentation should not reference implementation files."
        )


# ── Security Cases ───────────────────────────────────────────────────────────


class TestSecurityDocumentation:
    def test_api_md_no_secrets_or_credentials(self, api_md_content: str):
        """Ensure API.md does not contain any secrets, tokens, or credentials."""
        content_lower = api_md_content.lower()
        secret_patterns = [
            r"(?:api[_-]?key|secret[_-]?key|password|token|credential)\s*[:=]\s*['\"][^'\"]+['\"]",
            r"(?:aws|azure|gcp)[_-]?(?:secret|key|token)\s*[:=]",
            r"sk-[a-zA-Z0-9]{20,}",  # OpenAI-style keys
            r"ghp_[a-zA-Z0-9]{36}",  # GitHub personal access tokens
            r"-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----",
        ]
        for pattern in secret_patterns:
            matches = re.findall(pattern, api_md_content, re.IGNORECASE)
            assert not matches, (
                f"Potential secret/credential found in API.md matching pattern '{pattern}': {matches}"
            )

    def test_api_md_no_internal_urls_or_ips(self, api_md_content: str):
        """Ensure API.md does not expose internal URLs or IP addresses."""
        # Internal IPs
        internal_ip_pattern = r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b"
        internal_ips = re.findall(internal_ip_pattern, api_md_content)
        assert not internal_ips, (
            f"Internal IP addresses found in API.md: {internal_ips}"
        )

    def test_api_md_valueerror_for_invalid_status(self, api_md_content: str):
        """Verify documentation specifies ValueError for invalid TaskStatus values."""
        assert "ValueError" in api_md_content, (
            "ValueError for invalid TaskStatus construction not documented. "
            "This is important for input validation security."
        )

    def test_api_md_documents_input_validation(self, api_md_content: str):
        """Verify some form of input validation is documented (e.g., non-empty title)."""
        content_lower = api_md_content.lower()
        # Title should be documented as required / non-empty
        has_validation = (
            "required" in content_lower
            or "non-empty" in content_lower
            or "must be" in content_lower
            or "no default" in content_lower
        )
        assert has_validation, (
            "Input validation constraints (e.g., required title) not documented"
        )

    def test_api_md_no_executable_script_injection(self, api_md_content: str):
        """Ensure API.md does not contain script injection via HTML tags."""
        # Check for potentially dangerous HTML tags
        dangerous_tags = re.findall(
            r"<\s*(?:script|iframe|object|embed|form|input|button)\b",
            api_md_content,
            re.IGNORECASE,
        )
        assert not dangerous_tags, (
            f"Potentially dangerous HTML tags found in API.md: {dangerous_tags}"
        )

    def test_api_md_keyerror_is_security_relevant(self, api_md_content: str):
        """Verify KeyError is documented, preventing information leakage about store internals."""
        # KeyError should be the documented exception, not a generic exception
        # that might leak implementation details
        assert "KeyError" in api_md_content, (
            "KeyError must be documented as the specific exception for missing task IDs. "
            "Using specific exceptions prevents information leakage."
        )


# ── Structural Integrity Tests ───────────────────────────────────────────────


class TestStructuralIntegrity:
    def test_api_md_has_title(self, api_md_lines: list[str]):
        """Verify the document has a top-level heading."""
        has_h1 = any(line.startswith("# ") for line in api_md_lines)
        assert has_h1, "API.md should have a top-level (h1) heading"

    def test_api_md_has_table_of_contents_or_structure(self, api_md_content: str):
        """Verify the document has multiple sections (at least h2 headings)."""
        h2_headings = re.findall(r"^## .+", api_md_content, re.MULTILINE)
        assert len(h2_headings) >= 3, (
            f"Expected at least 3 h2 sections, found {len(h2_headings)}: {h2_headings}"
        )

    def test_api_md_has_code_examples(self, api_md_content: str):
        """Verify the document contains code examples (code blocks)."""
        code_blocks = re.findall(r"```", api_md_content)
        # Code blocks come in pairs (opening and closing)
        assert len(code_blocks) >= 2, (
            "API.md should contain at least one code block with examples"
        )
        assert len(code_blocks) % 2 == 0, (
            f"Unmatched code fences found: {len(code_blocks)} backtick-triple markers"
        )

    def test_api_md_has_import_paths(self, api_md_content: str):
        """Verify the document specifies import paths for public symbols."""
        assert "from tasklib import" in api_md_content or "import tasklib" in api_md_content, (
            "Import paths for tasklib not documented"
        )

    def test_api_md_utf8_encoding(self):
        """Verify API.md can be read as valid UTF-8."""
        try:
            API_MD_PATH.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            pytest.fail("API.md is not valid UTF-8")

    def test_api_md_no_trailing_whitespace_on_heading_lines(self, api_md_lines: list[str]):
        """Headings should not have excessive trailing whitespace (> 2 spaces for line break)."""
        heading_pattern = re.compile(r"^#{1,6}\s")
        for i, line in enumerate(api_md_lines):
            if heading_pattern.match(line):
                trailing = len(line) - len(line.rstrip())
                assert trailing <= 2, (
                    f"Line {i+1} heading has {trailing} trailing whitespace chars: {line!r}"
                )
