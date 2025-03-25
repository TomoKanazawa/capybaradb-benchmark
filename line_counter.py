#!/usr/bin/env python3
import re
import sys
from pathlib import Path

def count_code_lines(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        content = file.readlines()
    
    total_lines = len(content)
    empty_lines = 0
    comment_lines = 0
    import_lines = 0
    
    # Track if we're in a multi-line comment/string
    in_multiline_comment = False
    in_sql_block = False
    
    for line in content:
        line = line.strip()
        
        # Empty line check
        if not line:
            empty_lines += 1
            continue
            
        # Import statement check
        if re.match(r'^import\s+|^from\s+\w+\s+import', line):
            import_lines += 1
            continue

        # Check for SQL block start/end patterns
        sql_start_pattern = re.compile(r'cur\.execute\(\s*"""')
        sql_end_pattern = re.compile(r'"""\s*[,)]')
        
        # Handle SQL blocks inside triple quotes
        if not in_sql_block and sql_start_pattern.search(line):
            in_sql_block = True
            if sql_end_pattern.search(line):
                # SQL query is on a single line
                in_sql_block = False
            continue
            
        if in_sql_block:
            if sql_end_pattern.search(line):
                in_sql_block = False
            continue
            
        # Handle multi-line comments/strings for Python (that are not SQL blocks)
        if (line.startswith('"""') or line.startswith("'''")) and not in_sql_block:
            if line.endswith('"""') and len(line) > 3 and not line.endswith('""""') or \
               line.endswith("'''") and len(line) > 3 and not line.endswith("''''"):
                # Single line docstring
                comment_lines += 1
                continue
            else:
                in_multiline_comment = not in_multiline_comment
                comment_lines += 1
                continue
                
        if in_multiline_comment:
            if line.endswith('"""') or line.endswith("'''"):
                in_multiline_comment = False
            comment_lines += 1
            continue
            
        # Single line comment check
        if line.startswith('#'):
            comment_lines += 1
            continue
            
        # Line with code and trailing comment
        if '#' in line and not re.search(r'["\'].*#.*["\']', line):
            # Don't count if # is within a string
            code_part = line.split('#')[0].strip()
            if code_part:
                # There's actual code before the comment
                continue
            else:
                # It's just a comment line
                comment_lines += 1
                continue
    
    actual_code_lines = total_lines - empty_lines - comment_lines - import_lines
    return {
        'total_lines': total_lines,
        'empty_lines': empty_lines,
        'comment_lines': comment_lines,
        'import_lines': import_lines,
        'actual_code_lines': actual_code_lines,
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python line_counter.py <file_path> [<file_path> ...]")
        sys.exit(1)
        
    grand_total = {
        'total_lines': 0,
        'empty_lines': 0,
        'comment_lines': 0,
        'import_lines': 0,
        'actual_code_lines': 0,
    }
    
    for file_arg in sys.argv[1:]:
        path = Path(file_arg)
        if path.is_file():
            result = count_code_lines(path)
            
            print(f"\nFile: {path}")
            print(f"Total lines: {result['total_lines']}")
            print(f"Empty lines: {result['empty_lines']}")
            print(f"Comment lines: {result['comment_lines']}")
            print(f"Import lines: {result['import_lines']}")
            print(f"Actual code lines: {result['actual_code_lines']}")
            
            # Add to grand total
            for key in grand_total:
                grand_total[key] += result[key]
        else:
            print(f"Error: '{path}' is not a valid file")
    
    # If multiple files were processed, show the grand total
    if len(sys.argv) > 2:
        print("\n=== SUMMARY ===")
        print(f"Total lines: {grand_total['total_lines']}")
        print(f"Empty lines: {grand_total['empty_lines']}")
        print(f"Comment lines: {grand_total['comment_lines']}")
        print(f"Import lines: {grand_total['import_lines']}")
        print(f"Actual code lines: {grand_total['actual_code_lines']}")

if __name__ == "__main__":
    main()
