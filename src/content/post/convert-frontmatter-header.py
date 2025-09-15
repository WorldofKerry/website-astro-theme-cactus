import re
import yaml
from datetime import datetime
from pathlib import Path


def parse_mdx_frontmatter(content):
    """
    Parse MDX frontmatter from file content.
    Returns tuple of (frontmatter_dict, remaining_content)
    """
    # Match frontmatter between --- delimiters
    frontmatter_pattern = r"^---\n(.*?)\n---\n(.*)"
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if not match:
        return None, content

    frontmatter_yaml = match.group(1)
    remaining_content = match.group(2)

    try:
        frontmatter = yaml.safe_load(frontmatter_yaml)
        return frontmatter, remaining_content
    except yaml.YAMLError as e:
        print(f"Error parsing YAML frontmatter: {e}")
        return None, content


def convert_date_format(date_string):
    """
    Convert date from '2023-03-22T00:00:00-0800' format to 'DD MMM YYYY' format
    """
    try:
        # Parse the ISO format date
        dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        # Format to desired output
        return dt.strftime("%d %b %Y")
    except (ValueError, AttributeError):
        # If parsing fails, return original string
        return date_string


def convert_frontmatter(old_frontmatter):
    """
    Convert old frontmatter format to new format
    """
    new_frontmatter = {}

    # Copy title as-is but change quotes from single to double
    if "title" in old_frontmatter:
        new_frontmatter["title"] = str(old_frontmatter["title"])

    # Convert summary to description
    if "summary" in old_frontmatter:
        new_frontmatter["description"] = str(old_frontmatter["summary"])

    # Convert date to publishDate with new format
    if "date" in old_frontmatter:
        new_frontmatter["publishDate"] = convert_date_format(old_frontmatter["date"])

    # Convert tags format (keep as array but ensure proper format)
    if "tags" in old_frontmatter:
        new_frontmatter["tags"] = old_frontmatter["tags"]

    # Copy other fields that might be useful
    if "draft" in old_frontmatter and old_frontmatter["draft"]:
        new_frontmatter["draft"] = old_frontmatter["draft"]

    return new_frontmatter


def frontmatter_to_yaml(frontmatter):
    """
    Convert frontmatter dictionary back to YAML string with proper formatting
    """
    # Custom serialization to control quote style
    yaml_lines = []

    for key, value in frontmatter.items():
        if isinstance(value, str):
            # Use double quotes for strings
            yaml_lines.append(f'{key}: "{value}"')
        elif isinstance(value, list):
            # Handle arrays
            yaml_lines.append(
                f"{key}: {yaml.dump(value, default_flow_style=True).strip()}"
            )
        else:
            # Handle other types (bool, int, etc.)
            yaml_lines.append(f"{key}: {yaml.dump(value).strip()}")

    return "\n".join(yaml_lines)


def convert_mdx_file(file_path, output_path=None):
    """
    Convert a single MDX file from old format to new format
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        frontmatter, body = parse_mdx_frontmatter(content)

        if frontmatter is None:
            print(f"No frontmatter found in {file_path}")
            return False

        # Convert frontmatter
        new_frontmatter = convert_frontmatter(frontmatter)

        # Generate new content
        new_yaml = frontmatter_to_yaml(new_frontmatter)
        new_content = f"---\n{new_yaml}\n---\n{body}"

        # Write to output file
        if output_path is None:
            output_path = file_path

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"Successfully converted {file_path}")
        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def convert_directory(directory_path, file_pattern="*.mdx"):
    """
    Convert all MDX files in a directory
    """
    directory = Path(directory_path)
    files = list(directory.glob(file_pattern))

    if not files:
        print(f"No {file_pattern} files found in {directory_path}")
        return

    success_count = 0
    for file_path in files:
        if convert_mdx_file(file_path):
            success_count += 1

    print(f"Converted {success_count}/{len(files)} files successfully")


# Example usage
if __name__ == "__main__":
    # Test with the example content
    test_content = """---
title: 'Pointer Problems'
date: '2023-03-22T00:00:00-0800'
tags: ['life', 'programming']
draft: true
summary: 'Perplexing predicaments with pointers: A plethora of practical problems for practicing programmers to ponder.'
layout: PostSimple
---

# Your MDX content here

This is the body of your MDX file.
"""

    print("Testing with example content:")
    print("=" * 50)

    frontmatter, body = parse_mdx_frontmatter(test_content)
    if frontmatter:
        print("Original frontmatter:")
        print(yaml.dump(frontmatter, default_flow_style=False))

        new_frontmatter = convert_frontmatter(frontmatter)
        print("\nConverted frontmatter:")
        print(frontmatter_to_yaml(new_frontmatter))

        new_content = f"---\n{frontmatter_to_yaml(new_frontmatter)}\n---\n{body}"
        print("\nFull converted content:")
        print(new_content)

    # Uncomment the lines below to convert actual files
    # convert_mdx_file("example.mdx", "example_converted.mdx")
    convert_directory("./", "*.mdx")
