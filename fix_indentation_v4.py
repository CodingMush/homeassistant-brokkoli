#!/usr/bin/env python3
"""Fix indentation in services.py"""

def fix_indentation():
    with open('custom_components/plant/services.py', 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Fix the specific for loop issue
        if line.strip() == 'for sensor_key in [FLOW_SENSOR_TEMPERATURE, FLOW_SENSOR_MOISTURE, FLOW_SENSOR_CONDUCTIVITY,':
            fixed_lines.append(line)
            i += 1
            # Next line should be continuation of the for statement
            if i < len(lines) and 'FLOW_SENSOR_ILLUMINANCE' in lines[i]:
                fixed_lines.append(lines[i])
                i += 1
                # Next line should be the if statement indented properly
                if i < len(lines) and 'if sensor_key in plant_info:' in lines[i]:
                    # Fix the indentation
                    fixed_lines.append('        ' + lines[i].lstrip())
                    i += 1
                    # Next line should be indented further
                    if i < len(lines):
                        fixed_lines.append('            ' + lines[i].lstrip())
                        i += 1
                continue
        
        # Fix other specific indentation issues
        if line.strip() == 'except Exception as e:':
            fixed_lines.append('        ' + line.lstrip())
            i += 1
            continue
            
        fixed_lines.append(line)
        i += 1
    
    with open('custom_components/plant/services.py', 'w') as f:
        f.writelines(fixed_lines)

if __name__ == '__main__':
    fix_indentation()
    print("Indentation fixed!")