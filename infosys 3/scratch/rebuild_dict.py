import os
import re
import ast

# Read expand_multilingual.py
with open("scratch/expand_multilingual.py", "r", encoding="utf-8") as f:
    em_content = f.read()

# Extract expanded_dict_str
# It starts at expanded_dict_str = """MULTILINGUAL_DICTIONARY = {
# and ends at }"""
em_match = re.search(r'expanded_dict_str = """MULTILINGUAL_DICTIONARY = (\{.*?\}?)"""', em_content, re.DOTALL)
if not em_match:
    print("Could not find expanded_dict_str")
    exit(1)
em_dict_str = em_match.group(1)

# Read add_conversations.py
with open("scratch/add_conversations.py", "r", encoding="utf-8") as f:
    ac_content = f.read()
ac_match = re.search(r'new_categories_str = """(.*?)"""', ac_content, re.DOTALL)
if not ac_match:
    print("Could not find new_categories_str")
    exit(1)
ac_dict_str = ac_match.group(1)

# Read add_native_fluent.py
with open("scratch/add_native_fluent.py", "r", encoding="utf-8") as f:
    anf_content = f.read()
anf_match = re.search(r'native_categories_str = """(.*?)"""', anf_content, re.DOTALL)
if not anf_match:
    print("Could not find native_categories_str")
    exit(1)
anf_dict_str = anf_match.group(1)

# Parse them into python dictionaries using ast.literal_eval
dict1 = ast.literal_eval("{" + em_dict_str.strip().lstrip('{').rstrip('}') + "}")
dict2 = ast.literal_eval("{" + ac_dict_str.strip() + "}")
dict3 = ast.literal_eval("{" + anf_dict_str.strip() + "}")

# Merge them
merged_dict = {}
merged_dict.update(dict1)
merged_dict.update(dict2)
merged_dict.update(dict3)

print("Merged keys:", list(merged_dict.keys()))

# Custom formatter to output valid python representation of the dict with nice formatting
def format_value(val, indent=0):
    space = " " * indent
    if isinstance(val, dict):
        items = []
        for k, v in val.items():
            formatted_k = repr(k)
            formatted_v = format_value(v, indent + 4)
            items.append(f"{space}    {formatted_k}: {formatted_v.lstrip()}")
        return "{\n" + ",\n".join(items) + "\n" + space + "}"
    elif isinstance(val, list):
        items = []
        for item in val:
            items.append(format_value(item, indent + 4))
        return "[\n" + ",\n".join(items) + "\n" + space + "]"
    elif isinstance(val, tuple):
        # Format tuple: e.g. ("Hello", "hello")
        return repr(val)
    else:
        return repr(val)

formatted_dict = "MULTILINGUAL_DICTIONARY = " + format_value(merged_dict, 0)

# Now, read language_learning_service.py and replace the broken MULTILINGUAL_DICTIONARY block
with open("language_learning_service.py", "r", encoding="utf-8") as f:
    lls_content = f.read()

# We need to find "MULTILINGUAL_DICTIONARY = {" and match brace count to find the end
start_idx = lls_content.find("MULTILINGUAL_DICTIONARY = {")
if start_idx == -1:
    print("Could not find MULTILINGUAL_DICTIONARY in language_learning_service.py")
    exit(1)

# Let's count open/close braces to find the end of the dictionary
# To be robust, let's scan forward from start_idx
open_braces = 0
end_idx = None
for idx in range(start_idx, len(lls_content)):
    char = lls_content[idx]
    if char == '{':
        open_braces += 1
    elif char == '}':
        open_braces -= 1
        if open_braces == 0:
            end_idx = idx
            break

if end_idx is None:
    print("Could not find the end of MULTILINGUAL_DICTIONARY")
    # Let's try searching for the function definition get_db_connection()
    db_conn_idx = lls_content.find("def get_db_connection():")
    if db_conn_idx != -1:
        # End is just before that
        end_idx = db_conn_idx - 1
        while end_idx > start_idx and lls_content[end_idx] not in ('}', '\n'):
            end_idx -= 1
    else:
        exit(1)

# Replace the dictionary block
new_lls_content = lls_content[:start_idx] + formatted_dict + lls_content[end_idx + 1:]

# Also fix the duplicate categories in get_or_create_language_pair
# Since old_categories_block has multiline spaces, let's replace it by matching lines:
cat_pattern = r'categories\s*=\s*\[[^\]]*?\]'
new_categories_block = """categories = [
            "Greetings", "Numbers", "Colors", "Family", "Food", 
            "Animals", "Daily Objects", "Daily Conversations", 
            "Sentence Practice", "Story Reading", 
            "At the Market", "Asking for Directions", "At the Doctor", "Workspace Conversations",
            "Idioms & Daily Slang", "Socializing & Hobbies", "Advanced Workplace & Debate"
        ]"""

new_lls_content = re.sub(cat_pattern, new_categories_block, new_lls_content, count=1)

with open("language_learning_service.py", "w", encoding="utf-8") as f:
    f.write(new_lls_content)

print("Successfully rebuilt language_learning_service.py!")
