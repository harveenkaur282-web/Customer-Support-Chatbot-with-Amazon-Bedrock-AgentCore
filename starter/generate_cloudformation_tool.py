#!/usr/bin/env python3
"""
Generate cloudformation-tool.yaml by inlining create_bug_report.py.

Usage:
    python generate_cloudformation_tool.py

Edit cloudformation-tool-base.yaml and create_bug_report.py, then run this
script to regenerate cloudformation-tool.yaml. Do not edit it directly.

Note on $ signs
---------------
cloudformation-tool-base.yaml uses Python string.Template syntax: $var or
${var} marks a placeholder. This script uses safe_substitute(), so any ${...}
patterns that are not recognised placeholder names (e.g. CloudFormation !Sub
variables like ${Suffix}) are left unchanged in the output.

If you ever need a literal $ followed by a recognised placeholder name, write
$$ in the base template (e.g. $$create_bug_report produces $create_bug_report).
"""
from pathlib import Path
from string import Template

SCRIPT_DIR = Path(__file__).parent
BASE_TEMPLATE = SCRIPT_DIR / "cloudformation-tool-base.yaml"
OUTPUT_TEMPLATE = SCRIPT_DIR / "cloudformation-tool.yaml"

GENERATED_HEADER = """\
# Auto-generated from cloudformation-tool-base.yaml — do not edit directly.
# To regenerate: edit cloudformation-tool-base.yaml and create_bug_report.py,
# then run:
#   python generate_cloudformation_tool.py

"""


def indented(path: Path, spaces: int = 10) -> str:
    """Read a Python file and indent every non-blank line by `spaces` spaces."""
    pad = ' ' * spaces
    lines = path.read_text().rstrip('\n').splitlines()
    return '\n'.join(pad + line if line.strip() else '' for line in lines)


def generate() -> None:
    result = Template(BASE_TEMPLATE.read_text()).safe_substitute(
        create_bug_report=indented(SCRIPT_DIR / 'create_bug_report.py'),
    )
    OUTPUT_TEMPLATE.write_text(GENERATED_HEADER + result)
    print(f"Generated {OUTPUT_TEMPLATE.name}")


if __name__ == '__main__':
    generate()