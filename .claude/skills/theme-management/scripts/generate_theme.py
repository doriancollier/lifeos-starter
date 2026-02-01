#!/usr/bin/env python3
"""
Theme Generator for LifeOS
Generates synchronized VS Code and Obsidian themes from palette definitions.

Usage:
    python generate_theme.py <theme_name> [--project-dir PATH]
    python generate_theme.py --from-color <hex> --name <theme_name> [--project-dir PATH]
    python generate_theme.py --list [--project-dir PATH]

The script:
1. Loads palette from palettes.yaml or user themes
2. Computes derived colors (hover, alpha variants)
3. Generates VS Code colorCustomizations
4. Generates Obsidian themed-chrome.css
5. Updates both editor configurations
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip3 install pyyaml")
    sys.exit(1)


def get_project_dir(override=None):
    """Get project directory from argument, env var, or cwd."""
    if override:
        return Path(override)
    if "CLAUDE_PROJECT_DIR" in os.environ:
        return Path(os.environ["CLAUDE_PROJECT_DIR"])
    return Path.cwd()


def load_palettes(project_dir):
    """Load built-in palettes from palettes.yaml."""
    palettes_path = project_dir / ".claude/skills/theme-management/palettes.yaml"
    if not palettes_path.exists():
        print(f"Error: Palettes file not found: {palettes_path}")
        sys.exit(1)

    with open(palettes_path, 'r') as f:
        return yaml.safe_load(f)


def load_user_themes(project_dir):
    """Load custom user themes from .user/themes.yaml."""
    themes_path = project_dir / ".user/themes.yaml"
    if not themes_path.exists():
        return {"custom_themes": {}}

    with open(themes_path, 'r') as f:
        return yaml.safe_load(f) or {"custom_themes": {}}


def get_palette(name, project_dir):
    """Get palette by name from built-in or user themes."""
    data = load_palettes(project_dir)
    palettes = data.get("palettes", {})

    if name in palettes:
        return palettes[name], "builtin"

    # Check user themes
    user_data = load_user_themes(project_dir)
    custom = user_data.get("custom_themes", {})

    if name in custom:
        return custom[name], "custom"

    return None, None


def list_themes(project_dir):
    """List all available themes."""
    data = load_palettes(project_dir)
    default = data.get("default_theme", "midnight")
    palettes = data.get("palettes", {})

    user_data = load_user_themes(project_dir)
    custom = user_data.get("custom_themes", {})

    print("\nAvailable Themes:")
    print("-" * 50)

    print("\nBuilt-in:")
    for name, p in palettes.items():
        marker = " (default)" if name == default else ""
        desc = p.get("description", "")
        print(f"  {name}{marker} - {desc}")

    if custom:
        print("\nCustom:")
        for name, p in custom.items():
            desc = p.get("description", p.get("name", ""))
            print(f"  {name} - {desc}")

    print()


def lighten_color(hex_color, percent):
    """Lighten a hex color by a percentage."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    r = min(255, int(r + (255 - r) * percent / 100))
    g = min(255, int(g + (255 - g) * percent / 100))
    b = min(255, int(b + (255 - b) * percent / 100))

    return f"#{r:02x}{g:02x}{b:02x}"


def darken_color(hex_color, percent):
    """Darken a hex color by a percentage."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    r = max(0, int(r * (100 - percent) / 100))
    g = max(0, int(g * (100 - percent) / 100))
    b = max(0, int(b * (100 - percent) / 100))

    return f"#{r:02x}{g:02x}{b:02x}"


def generate_palette_from_color(hex_color, name="personal"):
    """Generate a full palette from a single favorite color."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: #{hex_color}")

    accent = f"#{hex_color}"

    return {
        "name": name.title(),
        "description": f"Custom theme from {accent}",
        "primary": darken_color(accent, 40),
        "primaryInactive": darken_color(accent, 55),
        "secondary": darken_color(accent, 60),
        "tertiary": darken_color(accent, 75),
        "border": darken_color(accent, 30),
        "accent": accent,
        "accentLight": lighten_color(accent, 20),
    }


def compute_derived_colors(palette):
    """Compute derived colors from palette."""
    derived = dict(palette)

    # primaryHover: lighten primary by 15%
    derived["primaryHover"] = lighten_color(palette["primary"], 15)

    # Alpha variants (append hex alpha to accent)
    accent = palette["accent"].lstrip('#')
    derived["accentAlpha20"] = f"#{accent}20"
    derived["accentAlpha15"] = f"#{accent}15"

    return derived


def apply_template(template_content, colors, theme_name):
    """Replace placeholders in template with color values."""
    colors["themeName"] = theme_name

    result = template_content
    for key, value in colors.items():
        result = result.replace(f"{{{{{key}}}}}", value)

    return result


def generate_vscode_config(colors, project_dir):
    """Generate VS Code colorCustomizations."""
    template_path = project_dir / ".claude/skills/theme-management/templates/vscode-colors.json"

    with open(template_path, 'r') as f:
        template = f.read()

    # Replace placeholders
    for key, value in colors.items():
        template = template.replace(f"{{{{{key}}}}}", value)

    return json.loads(template)


def update_vscode_settings(color_config, project_dir):
    """Merge colorCustomizations into VS Code settings.json."""
    settings_path = project_dir / ".vscode/settings.json"

    if settings_path.exists():
        # Read existing settings (handle comments by stripping them)
        content = settings_path.read_text()
        # Remove single-line comments (crude but works for typical settings)
        content_no_comments = re.sub(r'^\s*//.*$', '', content, flags=re.MULTILINE)
        # Remove trailing commas before } or ]
        content_no_comments = re.sub(r',(\s*[}\]])', r'\1', content_no_comments)

        try:
            settings = json.loads(content_no_comments)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse {settings_path}, creating fresh config")
            settings = {}
    else:
        settings = {}
        settings_path.parent.mkdir(parents=True, exist_ok=True)

    # Merge colorCustomizations
    settings["workbench.colorCustomizations"] = color_config

    # Write back with nice formatting
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=4)

    print(f"Updated: {settings_path}")


def generate_obsidian_css(colors, theme_name, project_dir):
    """Generate Obsidian CSS snippet."""
    template_path = project_dir / ".claude/skills/theme-management/templates/obsidian-chrome.css"

    with open(template_path, 'r') as f:
        template = f.read()

    return apply_template(template, colors, theme_name)


def update_obsidian_config(css_content, project_dir):
    """Write Obsidian CSS and update appearance.json."""
    snippets_dir = project_dir / ".obsidian/snippets"
    snippets_dir.mkdir(parents=True, exist_ok=True)

    # Write CSS
    css_path = snippets_dir / "themed-chrome.css"
    with open(css_path, 'w') as f:
        f.write(css_content)
    print(f"Updated: {css_path}")

    # Update appearance.json
    appearance_path = project_dir / ".obsidian/appearance.json"

    if appearance_path.exists():
        with open(appearance_path, 'r') as f:
            appearance = json.load(f)
    else:
        appearance = {}

    # Enable themed-chrome snippet, remove old vscode-dark-red
    snippets = appearance.get("enabledCssSnippets", [])

    # Remove old snippet if present
    if "vscode-dark-red" in snippets:
        snippets.remove("vscode-dark-red")

    # Add themed-chrome if not present
    if "themed-chrome" not in snippets:
        snippets.append("themed-chrome")

    appearance["enabledCssSnippets"] = snippets

    with open(appearance_path, 'w') as f:
        json.dump(appearance, f, indent=2)
    print(f"Updated: {appearance_path}")


def save_user_theme(palette, name, project_dir):
    """Save a custom theme to .user/themes.yaml."""
    themes_path = project_dir / ".user/themes.yaml"

    if themes_path.exists():
        with open(themes_path, 'r') as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    if "custom_themes" not in data:
        data["custom_themes"] = {}

    data["custom_themes"][name] = palette

    with open(themes_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    print(f"Saved custom theme '{name}' to: {themes_path}")


def apply_theme(theme_name, project_dir, save_as_default=False):
    """Apply a theme by name."""
    palette, source = get_palette(theme_name, project_dir)

    if palette is None:
        print(f"Error: Theme '{theme_name}' not found")
        list_themes(project_dir)
        sys.exit(1)

    print(f"\nApplying theme: {theme_name} ({source})")

    # Compute derived colors
    colors = compute_derived_colors(palette)

    # Generate and apply VS Code config
    vscode_config = generate_vscode_config(colors, project_dir)
    update_vscode_settings(vscode_config, project_dir)

    # Generate and apply Obsidian CSS
    obsidian_css = generate_obsidian_css(colors, theme_name, project_dir)
    update_obsidian_config(obsidian_css, project_dir)

    print(f"\nTheme '{theme_name}' applied successfully!")
    print("- VS Code: Reload window to see changes")
    print("- Obsidian: Changes apply immediately")


def main():
    parser = argparse.ArgumentParser(description="Generate synchronized VS Code + Obsidian themes")
    parser.add_argument("theme", nargs="?", help="Theme name to apply")
    parser.add_argument("--list", action="store_true", help="List available themes")
    parser.add_argument("--from-color", metavar="HEX", help="Generate theme from a hex color")
    parser.add_argument("--name", metavar="NAME", help="Name for generated theme")
    parser.add_argument("--save", action="store_true", help="Save generated theme to user themes")
    parser.add_argument("--project-dir", metavar="PATH", help="Project directory path")

    args = parser.parse_args()
    project_dir = get_project_dir(args.project_dir)

    if args.list:
        list_themes(project_dir)
        return

    if args.from_color:
        name = args.name or "personal"
        print(f"\nGenerating theme from color: {args.from_color}")

        try:
            palette = generate_palette_from_color(args.from_color, name)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

        if args.save:
            save_user_theme(palette, name, project_dir)

        # Apply the generated theme
        colors = compute_derived_colors(palette)

        vscode_config = generate_vscode_config(colors, project_dir)
        update_vscode_settings(vscode_config, project_dir)

        obsidian_css = generate_obsidian_css(colors, name, project_dir)
        update_obsidian_config(obsidian_css, project_dir)

        print(f"\nTheme '{name}' generated and applied!")
        return

    if args.theme:
        apply_theme(args.theme, project_dir)
        return

    # No arguments - show usage
    parser.print_help()


if __name__ == "__main__":
    main()
