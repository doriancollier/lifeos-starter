#!/usr/bin/env python3
"""
Tests for inject_placeholders.py

Run with: python3 test_inject_placeholders.py
"""

import unittest
import tempfile
import os
from pathlib import Path

# Import the module under test
from inject_placeholders import (
    flatten_dict,
    build_placeholder_map,
    inject_placeholders,
    add_runtime_placeholders,
)


class TestFlattenDict(unittest.TestCase):
    """Tests for flatten_dict function."""

    def test_simple_dict(self):
        """Flat dict should remain unchanged."""
        d = {"name": "John", "age": 30}
        result = flatten_dict(d)
        self.assertEqual(result["name"], "John")
        self.assertEqual(result["age"], 30)

    def test_nested_dict(self):
        """Nested dict should be flattened with underscores."""
        d = {"user": {"name": "John", "email": "john@example.com"}}
        result = flatten_dict(d)
        self.assertEqual(result["user_name"], "John")
        self.assertEqual(result["user_email"], "john@example.com")

    def test_deeply_nested(self):
        """Deeply nested dicts should flatten correctly."""
        d = {"level1": {"level2": {"level3": "value"}}}
        result = flatten_dict(d)
        self.assertEqual(result["level1_level2_level3"], "value")

    def test_list_takes_first_item(self):
        """Lists should use the first item."""
        d = {"children": [{"name": "Alex"}, {"name": "Sam"}]}
        result = flatten_dict(d)
        self.assertEqual(result["children_name"], "Alex")

    def test_simple_list(self):
        """Simple list should use first item."""
        d = {"tags": ["python", "testing"]}
        result = flatten_dict(d)
        self.assertEqual(result["tags"], "python")

    def test_empty_list(self):
        """Empty list should return empty string."""
        d = {"items": []}
        result = flatten_dict(d)
        self.assertEqual(result["items"], "")

    def test_none_value(self):
        """None values should become empty string."""
        d = {"value": None}
        result = flatten_dict(d)
        self.assertEqual(result["value"], "")


class TestBuildPlaceholderMap(unittest.TestCase):
    """Tests for build_placeholder_map function."""

    def test_identity_config(self):
        """Identity config should map to expected placeholders."""
        config = {
            "user": {
                "name": "John Doe",
                "first_name": "John",
                "email": "john@example.com",
                "timezone": "America/Chicago",
            }
        }
        result = build_placeholder_map(config)
        self.assertEqual(result["user_name"], "John Doe")
        self.assertEqual(result["user_first_name"], "John")
        self.assertEqual(result["user_email"], "john@example.com")
        self.assertEqual(result["timezone"], "America/Chicago")

    def test_family_config(self):
        """Family config should map to expected placeholders."""
        config = {
            "family": {
                "partner_name": "Jane",
                "children": [{"name": "Alex"}],
            }
        }
        result = build_placeholder_map(config)
        self.assertEqual(result["partner_name"], "Jane")
        self.assertEqual(result["child_name"], "Alex")

    def test_companies_config(self):
        """Companies config should map to expected placeholders."""
        config = {
            "companies": {
                "company_1": {"name": "Acme Corp"},
                "company_2": {"name": "Side Project"},
                "company_3": {"name": "Family Venture"},
            }
        }
        result = build_placeholder_map(config)
        self.assertEqual(result["company_1_name"], "Acme Corp")
        self.assertEqual(result["company_2_name"], "Side Project")
        self.assertEqual(result["company_3_name"], "Family Venture")

    def test_coaching_config(self):
        """Coaching config should map to expected placeholders."""
        config = {"coaching": {"intensity": 7}}
        result = build_placeholder_map(config)
        self.assertEqual(result["coaching_intensity"], "7")

    def test_missing_values_are_empty_string(self):
        """Missing config values should result in empty strings."""
        config = {}
        result = build_placeholder_map(config)
        self.assertEqual(result["user_name"], "")
        self.assertEqual(result["partner_name"], "")
        self.assertEqual(result["company_1_name"], "")


class TestInjectPlaceholders(unittest.TestCase):
    """Tests for inject_placeholders function."""

    def test_simple_replacement(self):
        """Simple placeholder should be replaced."""
        template = "Hello, {{user_name}}!"
        placeholders = {"user_name": "John"}
        result = inject_placeholders(template, placeholders)
        self.assertEqual(result, "Hello, John!")

    def test_multiple_replacements(self):
        """Multiple placeholders should all be replaced."""
        template = "{{user_name}} lives in {{timezone}}"
        placeholders = {"user_name": "John", "timezone": "America/Chicago"}
        result = inject_placeholders(template, placeholders)
        self.assertEqual(result, "John lives in America/Chicago")

    def test_repeated_placeholder(self):
        """Same placeholder used multiple times should all be replaced."""
        template = "{{name}} and {{name}} again"
        placeholders = {"name": "John"}
        result = inject_placeholders(template, placeholders)
        self.assertEqual(result, "John and John again")

    def test_unknown_placeholder_preserved(self):
        """Unknown placeholders should be preserved as-is."""
        template = "Hello, {{unknown_placeholder}}!"
        placeholders = {"user_name": "John"}
        result = inject_placeholders(template, placeholders)
        self.assertEqual(result, "Hello, {{unknown_placeholder}}!")

    def test_empty_value_replacement(self):
        """Empty string values should replace placeholder with nothing."""
        template = "Name: {{user_name}}"
        placeholders = {"user_name": ""}
        result = inject_placeholders(template, placeholders)
        self.assertEqual(result, "Name: ")

    def test_multiline_template(self):
        """Multiline templates should work correctly."""
        template = """# Welcome {{user_name}}

Your timezone: {{timezone}}
Partner: {{partner_name}}"""
        placeholders = {
            "user_name": "John",
            "timezone": "America/Chicago",
            "partner_name": "Jane",
        }
        result = inject_placeholders(template, placeholders)
        expected = """# Welcome John

Your timezone: America/Chicago
Partner: Jane"""
        self.assertEqual(result, expected)

    def test_placeholder_in_code_block(self):
        """Placeholders in code blocks should still be replaced."""
        template = "```\npath={{vault_path}}\n```"
        placeholders = {"vault_path": "/Users/john/vault"}
        result = inject_placeholders(template, placeholders)
        self.assertEqual(result, "```\npath=/Users/john/vault\n```")


class TestAddRuntimePlaceholders(unittest.TestCase):
    """Tests for add_runtime_placeholders function."""

    def test_vault_path_added(self):
        """vault_path should be added from vault_root."""
        placeholders = {}
        vault_root = Path("/Users/john/vault")
        result = add_runtime_placeholders(placeholders, vault_root)
        self.assertEqual(result["vault_path"], "/Users/john/vault")

    def test_current_year_added(self):
        """current_year should be added."""
        placeholders = {}
        vault_root = Path("/tmp")
        result = add_runtime_placeholders(placeholders, vault_root)
        self.assertIn("current_year", result)
        # Should be a 4-digit year
        self.assertEqual(len(result["current_year"]), 4)
        self.assertTrue(result["current_year"].isdigit())

    def test_existing_placeholders_preserved(self):
        """Existing placeholders should not be overwritten."""
        placeholders = {"user_name": "John"}
        vault_root = Path("/tmp")
        result = add_runtime_placeholders(placeholders, vault_root)
        self.assertEqual(result["user_name"], "John")


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple functions."""

    def test_full_config_to_template(self):
        """Full workflow from config to template injection."""
        config = {
            "user": {
                "name": "John Doe",
                "first_name": "John",
                "email": "john@example.com",
                "timezone": "America/Chicago",
            },
            "family": {
                "partner_name": "Jane",
                "children": [{"name": "Alex"}],
            },
            "companies": {
                "company_1": {"name": "Acme Corp"},
            },
            "coaching": {"intensity": 7},
        }

        template = """# Welcome {{user_first_name}}

You work at {{company_1_name}}.
Your partner is {{partner_name}} and your child is {{child_name}}.
Coaching level: {{coaching_intensity}}
Timezone: {{timezone}}
Vault: {{vault_path}}"""

        placeholders = build_placeholder_map(config)
        placeholders = add_runtime_placeholders(placeholders, Path("/Users/john/vault"))
        result = inject_placeholders(template, placeholders)

        self.assertIn("Welcome John", result)
        self.assertIn("Acme Corp", result)
        self.assertIn("Jane", result)
        self.assertIn("Alex", result)
        self.assertIn("7", result)
        self.assertIn("America/Chicago", result)
        self.assertIn("/Users/john/vault", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
