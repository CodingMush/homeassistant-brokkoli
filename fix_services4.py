# Script to fix indentation error in services.py
with open('custom_components/plant/services.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the problematic section
start = content.find('                if entity.config_entry_id == entry_id and entity.domain == DOMAIN:')
end = content.find('            # Letzte Chance: Suche nach einem State mit den richtigen Attributen')

# Fix the indentation
fixed = content[:start] + content[start:end].replace('                ', '            ') + content[end:]

# Write the fixed content back to the file
with open('custom_components/plant/services.py', 'w', encoding='utf-8') as f:
    f.write(fixed)

print("Services file fixed successfully!")