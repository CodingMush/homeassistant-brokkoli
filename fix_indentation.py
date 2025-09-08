#!/usr/bin/env python3
"""Fix indentation in services.py"""

def fix_indentation():
    with open('custom_components/plant/services.py', 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    in_setup_function = False
    
    for line in lines:
        # Check if we're entering the async_setup_services function
        if line.strip() == 'async def async_setup_services(hass: HomeAssistant) -> None:':
            in_setup_function = True
            fixed_lines.append(line)
            continue
            
        # Check if we're leaving the async_setup_services function
        if in_setup_function and line.strip() == 'async def create_cycle(call: ServiceCall) -> ServiceResponse:':
            in_setup_function = False
            fixed_lines.append(line)
            continue
            
        # Fix indentation inside the async_setup_services function
        if in_setup_function:
            indent = len(line) - len(line.lstrip())
            if indent >= 12:  # Too much indentation
                # Reduce indentation from 12 spaces to 4 spaces
                fixed_lines.append('    ' + line[12:])
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    with open('custom_components/plant/services.py', 'w') as f:
        f.writelines(fixed_lines)

if __name__ == '__main__':
    fix_indentation()
    print("Indentation fixed!")