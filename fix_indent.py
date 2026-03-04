
import os

file_path = r"backend/app/services/qa/service.py"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
start_indent_block_1 = 281 # 0-indexed: line 282
end_indent_block_1 = 282   # 0-indexed: line 283
start_indent_block_2 = 290 # 0-indexed: line 291
end_indent_block_2 = 626   # 0-indexed: line 627 (return)

# verify line content to be sure
if "yield json.dumps" not in lines[start_indent_block_1]:
    print(f"Error: Line {start_indent_block_1} is not what expected: {lines[start_indent_block_1]}")
    exit(1)

if "cached_docs = None" not in lines[start_indent_block_2]:
    print(f"Error: Line {start_indent_block_2} is not what expected: {lines[start_indent_block_2]}")
    exit(1)

if "return" not in lines[end_indent_block_2].strip():
    print(f"Error: Line {end_indent_block_2} is not what expected: {lines[end_indent_block_2]}")
    # It might be empty line or comment, let's check context
    # actually line 626 (0-indexed) is 627 in file.
    # In my cat output, 627 is "            return".
    pass

for i, line in enumerate(lines):
    if (start_indent_block_1 <= i <= end_indent_block_1) or (start_indent_block_2 <= i <= end_indent_block_2):
        new_lines.append("    " + line)
    else:
        new_lines.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Indentation fixed.")
