import re
import sys
import os

def refactor_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content

    # Replace X | None with Optional[X]
    # We want to match things like "str | None", "List[int] | None", "dict[str, Any] | None"
    # The [^:|->=]+ part is tricky because we don't want to over-match.
    # Usually it's "Identifier | None" or "Generic[...] | None"
    
    # Let's use a regex that matches balanced brackets for the left side if possible, 
    # but for simplicity, we can match word characters and brackets.
    
    # This regex matches a "type-like" string followed by | None
    # Type-like: alphanumeric, underscore, dot, brackets, and quotes (for literal types)
    pattern = r'([\w\[\].\'"]+(?:\[[^\]]+\])?)\s*\|\s*None'
    
    # However, nested brackets like dict[str, list[int]] | None won't be fully matched by that.
    # Let's use a simpler approach: find " | None" and look backwards to find the start of the type.
    # Or just use a regex that handles one level of nesting which covers 99% of cases.
    nested_pattern = r'([\w\[\].\'"]+(?:\[[^\]\[]+(?:\[[^\]\[]+\])?[^\]\[]*\])?)\s*\|\s*None'
    
    new_content = re.sub(nested_pattern, r'Optional[\1]', content)
    
    # If there are still " | None" left, it might be deeper nesting. 
    # But let's see.
    
    if new_content != original_content:
        # Check if we need to add Optional to imports
        if 'Optional' not in original_content:
            # Find existing typing import
            typing_match = re.search(r'from typing import ([^#\n]+)', new_content)
            if typing_match:
                existing = typing_match.group(1)
                imports = [i.strip() for i in existing.split(',')]
                if 'Optional' not in imports:
                    imports.append('Optional')
                    imports.sort()
                    new_content = new_content.replace(typing_match.group(0), f"from typing import {', '.join(imports)}")
            else:
                # Add after __future__ or at top
                import_line = "from typing import Optional\n"
                future_match = re.search(r'from __future__ import annotations\n', new_content)
                if future_match:
                    new_content = new_content[:future_match.end()] + "\n" + import_line + new_content[future_match.end():]
                else:
                    new_content = import_line + "\n" + new_content

        with open(file_path, 'w') as f:
            f.write(new_content)
        return True
    return False

if __name__ == "__main__":
    count = 0
    for arg in sys.argv[1:]:
        if os.path.isfile(arg):
            if refactor_file(arg):
                count += 1
    print(f"Refactored {count} files")
