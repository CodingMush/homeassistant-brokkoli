# Script to fix syntax error in __init__.py
with open('custom_components/plant/__init__.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the problematic section
start = content.find('return unload_ok')
end = content.find('@websocket_api.websocket_command')

# Extract the problematic part
problematic = content[start:end]

# Fix the problematic part
fixed = 'return unload_ok\n\n'

# Replace the problematic part with the fixed version
new_content = content[:start] + fixed + content[end:]

# Write the fixed content back to the file
with open('custom_components/plant/__init__.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("File fixed successfully!")