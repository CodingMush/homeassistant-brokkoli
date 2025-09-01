# Script to fix syntax error in services.py
with open('custom_components/plant/services.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the problematic section
start = content.find('MIGRATE_TO_VIRTUAL_SENSORS_SCHEMA = vol.Schema')
# Find the end of the schema definition
end = content.find('except HomeAssistantError:')

# Extract the problematic part
problematic = content[start:end]

# Fix the problematic part by removing the orphaned except clauses
fixed = problematic

# Replace the problematic part with the fixed version
new_content = content[:start] + fixed + content[end+30:]  # Skip the orphaned except clauses

# Write the fixed content back to the file
with open('custom_components/plant/services.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Services file fixed successfully!")