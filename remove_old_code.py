#!/usr/bin/env python3
# Script to remove old rounding code from __init__.py

import os

# Read the file
file_path = 'custom_components/plant/__init__.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the lines to remove
start_line = None
end_line = None

for i, line in enumerate(lines):
    if '# Entfernt: Alte manuelle Rundungslogik' in line:
        start_line = i + 1  # Line after the comment
        break

if start_line is not None:
    # Find the end of the old code block
    for i in range(start_line, len(lines)):
        line = lines[i]
        if '    def _update_cycle_attributes(self) -> None:' in line:
            end_line = i
            break
    
    if end_line is not None:
        # Remove the old code block
        del lines[start_line:end_line]
        
        # Write the file back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("Old code removed successfully")
    else:
        print("Could not find end of code block")
else:
    print("Could not find start of old code block")