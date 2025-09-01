# Script to fix syntax error in services.py
with open('custom_components/plant/services.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the problematic section
start = content.find('vol.Optional(FLOW_MIGRATE_SENSORS, default=True): cv.boo')
end = content.find('async def async_setup_services')

# Fix the corrupted line
fixed = content[:start] + '    vol.Optional(FLOW_MIGRATE_SENSORS, default=True): cv.boolean,\n})\n\n' + content[end:]

# Write the fixed content back to the file
with open('custom_components/plant/services.py', 'w', encoding='utf-8') as f:
    f.write(fixed)

print("Services file fixed successfully!")