#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
from line_counter import count_code_lines

def get_implementation_files():
    """Return a list of all implementation files in the project"""
    implementation_files = []
    # Directories to search
    directories = ["capybaradb", "chroma", "langchain", "mongo", "pgvector", "pinecone"]
    
    # File extensions to include
    extensions = ['.py', '.js', '.ts', '.go', '.java', '.cpp', '.c', '.h', '.hpp', '.rs', '.sql']
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
            
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = Path(os.path.join(root, file))
                if file_path.suffix in extensions:
                    implementation_files.append(file_path)
    
    # Also include any implementation files in the root directory
    for file in os.listdir('.'):
        file_path = Path(file)
        if file_path.is_file() and file_path.suffix in extensions and file not in ['line_counter.py', 'count_all_files.py']:
            implementation_files.append(file_path)
    
    return implementation_files

def main():
    output_file = "line_count_results.txt"
    
    implementation_files = get_implementation_files()
    
    with open(output_file, 'w') as f:
        f.write("Line Count Results for Implementation Files\n")
        f.write("==========================================\n\n")
        
        for file_path in implementation_files:
            try:
                result = count_code_lines(file_path)
                
                file_info = f"\nFile: {file_path}\n"
                file_info += f"Total lines: {result['total_lines']}\n"
                file_info += f"Empty lines: {result['empty_lines']}\n"
                file_info += f"Comment lines: {result['comment_lines']}\n"
                file_info += f"Import lines: {result['import_lines']}\n"
                file_info += f"Actual code lines: {result['actual_code_lines']}\n"
                
                f.write(file_info)
                print(f"Processed: {file_path}")
                
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
        
        print("\nLine counting complete!")
        print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()