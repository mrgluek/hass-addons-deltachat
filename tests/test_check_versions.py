import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import check_versions  # noqa: E402

PLAIN_UPSTREAM = """# Changelog

## 2.12.1

- Fix for the new feature.

## 2.12.0

### Added
- New feature.

## 2.11.1

- Old fix.
"""

BRACKET_UPSTREAM = """# Changelog

## [Unreleased]

- Not released yet.

## [1.12.0] - 2026-10-16

- Username feature.

## [1.11.0] - 2026-10-10

- Intermediate release.

## [1.10.0] - 2026-10-01

- Already in the add-on.
"""


class TestExtractChangelogSections(unittest.TestCase):
    def test_plain_headings_multi_version(self):
        sections = check_versions.extract_changelog_sections(PLAIN_UPSTREAM, "2.11.1", "2.12.1")
        self.assertEqual([v for v, _ in sections], ["2.12.1", "2.12.0"])
        self.assertEqual(sections[0][1], "- Fix for the new feature.")
        self.assertEqual(sections[1][1], "### Added\n- New feature.")

    def test_bracket_headings_multi_version(self):
        sections = check_versions.extract_changelog_sections(BRACKET_UPSTREAM, "1.10.0", "1.12.0")
        self.assertEqual([v for v, _ in sections], ["1.12.0", "1.11.0"])
        self.assertEqual(sections[0][1], "- Username feature.")
        # The [Unreleased] body must not leak into any release
        self.assertNotIn("Not released", "".join(n for _, n in sections))

    def test_skips_versions_newer_than_target(self):
        sections = check_versions.extract_changelog_sections(PLAIN_UPSTREAM, "2.11.1", "2.12.0")
        self.assertEqual([v for v, _ in sections], ["2.12.0"])

    def test_numeric_ordering(self):
        text = "## 1.10.0\n- ten\n\n## 1.9.0\n- nine\n\n## 1.2.0\n- two\n"
        sections = check_versions.extract_changelog_sections(text, "1.1.0", "1.10.0")
        self.assertEqual([v for v, _ in sections], ["1.10.0", "1.9.0", "1.2.0"])

    def test_unknown_old_version_takes_only_target(self):
        sections = check_versions.extract_changelog_sections(PLAIN_UPSTREAM, "N/A", "2.12.1")
        self.assertEqual([v for v, _ in sections], ["2.12.1"])

    def test_empty_changelog(self):
        self.assertEqual(check_versions.extract_changelog_sections("", "1.0.0", "1.1.0"), [])


class TestSyncAddonVersion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addon = os.path.join(self.tmp, "demo")
        os.makedirs(self.addon)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _write_addon(self, version, changelog):
        with open(os.path.join(self.addon, "config.yaml"), "w", encoding="utf-8") as f:
            f.write(f'name: "Demo"\nversion: "{version}"\nslug: "demo"\n')
        with open(os.path.join(self.addon, "Dockerfile"), "w", encoding="utf-8") as f:
            f.write(f"FROM python:3.11-slim\nARG BOT_REF=v{version}\n")
        with open(os.path.join(self.addon, "CHANGELOG.md"), "w", encoding="utf-8") as f:
            f.write(changelog)

    def _read(self, name):
        with open(os.path.join(self.addon, name), encoding="utf-8") as f:
            return f.read()

    def _sync(self, new_ver, upstream):
        with patch.object(check_versions, "get_upstream_changelog", return_value=upstream):
            return check_versions.sync_addon_version("demo", new_ver, "deltachat_demo", addons_dir=self.tmp)

    def test_multi_version_jump_plain_headings(self):
        self._write_addon("2.11.1", "# Changelog\n\n## 2.11.1\n\n- Old fix.\n")
        self.assertTrue(self._sync("2.12.1", PLAIN_UPSTREAM))

        ch = self._read("CHANGELOG.md")
        self.assertTrue(ch.startswith("# Changelog\n\n## 2.12.1\n\n- Fix for the new feature.\n\n## 2.12.0\n\n### Added\n- New feature.\n\n## 2.11.1\n"))
        self.assertEqual(ch.count("## 2.11.1"), 1)
        self.assertIn('version: "2.12.1"', self._read("config.yaml"))
        self.assertIn("ARG BOT_REF=v2.12.1", self._read("Dockerfile"))

    def test_multi_version_jump_bracket_headings(self):
        self._write_addon("1.10.0", "# Changelog\n\n## 1.10.0\n\n- Already in the add-on.\n")
        self._sync("1.12.0", BRACKET_UPSTREAM)

        ch = self._read("CHANGELOG.md")
        # Converted to the add-on's "## X.Y.Z" style, newest first
        self.assertNotIn("[1.1", ch)
        self.assertLess(ch.index("## 1.12.0\n"), ch.index("## 1.11.0\n"))
        self.assertLess(ch.index("## 1.11.0\n"), ch.index("## 1.10.0\n"))
        self.assertIn("- Intermediate release.", ch)
        self.assertNotIn("Not released", ch)

    def test_skips_sections_already_in_addon_changelog(self):
        # 2.12.0 was added by hand earlier; only 2.12.1 is missing
        self._write_addon("2.11.1", "# Changelog\n\n## 2.12.0\n\n- Hand-written.\n\n## 2.11.1\n\n- Old fix.\n")
        self._sync("2.12.1", PLAIN_UPSTREAM)

        ch = self._read("CHANGELOG.md")
        self.assertEqual(ch.count("## 2.12.0"), 1)
        self.assertIn("- Hand-written.", ch)
        self.assertLess(ch.index("## 2.12.1"), ch.index("## 2.12.0"))

    def test_fallback_when_upstream_has_no_section(self):
        self._write_addon("1.0.0", "# Changelog\n\n## 1.0.0\n\n- First.\n")
        self._sync("1.0.1", "")

        ch = self._read("CHANGELOG.md")
        self.assertIn("## 1.0.1\n- Upstream update to version 1.0.1.\n", ch)

    def test_no_duplicate_when_target_already_present(self):
        original = "# Changelog\n\n## 2.12.1\n\n- Present.\n\n## 2.11.1\n\n- Old fix.\n"
        self._write_addon("2.11.1", original)
        self._sync("2.12.1", PLAIN_UPSTREAM)
        self.assertEqual(self._read("CHANGELOG.md"), original)


if __name__ == "__main__":
    unittest.main()
