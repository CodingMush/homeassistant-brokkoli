#!/usr/bin/env python3
"""Fix indentation in services.py"""

def fix_indentation():
    with open('custom_components/plant/services.py', 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    in_setup_function = False
    setup_indent_level = 0
    
    for i, line in enumerate(lines):
        # Check if we're entering the async_setup_services function
        if line.strip() == 'async def async_setup_services(hass: HomeAssistant) -> None:':
            in_setup_function = True
            setup_indent_level = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue
            
        # Check if we're leaving the async_setup_services function
        if in_setup_function:
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= setup_indent_level and line.strip() and not line.strip().startswith('#'):
                # We're leaving the function
                in_setup_function = False
                fixed_lines.append(line)
                continue
                
        # Fix indentation inside the async_setup_services function
        if in_setup_function and line.strip():
            current_indent = len(line) - len(line.lstrip())
            if current_indent > setup_indent_level:
                # Adjust indentation to be relative to the function start
                relative_indent = current_indent - setup_indent_level
                # Make sure we have proper 4-space indentation
                new_indent = setup_indent_level + ((relative_indent + 3) // 4) * 4
                fixed_lines.append(' ' * new_indent + line.lstrip())
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    with open('custom_components/plant/services.py', 'w') as f:
        f.writelines(fixed_lines)

if __name__ == '__main__':
    fix_indentation()
    print("Indentation fixed!")