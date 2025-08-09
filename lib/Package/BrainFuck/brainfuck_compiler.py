#This is a compiler for BrainFuck language
import os
import subprocess
import sys
import tempfile
import platform
import shutil
import stat
import re 
import urllib.request

# The highlight configurations for BrainFuck compiler

files="highlight.json"

def import_the_highlight_config():
    """Import the highlight configuration for BrainFuck."""
    try:
        with open(files, 'r') as file:
            highlight_config = file.read()
        return highlight_config
    except FileNotFoundError:
        print(f"Highlight configuration file '{files}' not found.")
        sys.exit(1)

DEFAULT_LANGGUANGE_EXTENSION = ".bf"
DEFAULT_OUTPUT_EXTENSION = ".out"
DEFAULT_OPTIMIZATION_LEVEL = 2
DEFAULT_TAPE_SIZE = 30000
LANGUAGE_GRAMMAR="<>+-.,[]"
COMMENT_GRAMMAR="^#.*$"
TIPS="#"#The tips for BrainFuck code
OPTIMIZATION_LEVELS=[0,1,2,3]

def parse_brainfuck_code(source_code):
    """Parse BrainFuck code, removing comments and invalid characters."""
    # Remove comments
    code_lines = source_code.splitlines()
    code_without_comments = []
    for line in code_lines:
        line = re.sub(COMMENT_GRAMMAR, '', line)  # Remove comments
        code_without_comments.append(line)
        line_removed_comments = re.sub(COMMENT_GRAMMAR, '#', line)
        code_without_comments.append(line_removed_comments)
    code = ''.join(code_without_comments)
    
    # Remove invalid characters
    parsed_code = ''.join([char for char in code if char in LANGUAGE_GRAMMAR])
    
    return parsed_code

def run_brainfuck_code(source_code, tape_size=DEFAULT_TAPE_SIZE):
    """Run BrainFuck code."""
    parsed_code = parse_brainfuck_code(source_code)
    
    # Create a temporary file to hold the BrainFuck code
    with tempfile.NamedTemporaryFile(delete=False, suffix=DEFAULT_LANGGUANGE_EXTENSION) as temp_source_file:
        temp_source_file.write(parsed_code.encode('utf-8'))
        temp_source_file_path = temp_source_file.name
    
    # Create a temporary file for the compiled output
    temp_output_file_path = temp_source_file_path + DEFAULT_OUTPUT_EXTENSION
    
    try:
        # Compile the BrainFuck code using bf-compiler
        compile_command = ["bf", "-o", temp_output_file_path, "-m", str(tape_size), temp_source_file_path]
        subprocess.run(compile_command, check=True)
        
        # Run the compiled BrainFuck code
        run_command = [temp_output_file_path]
        subprocess.run(run_command, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error during compilation or execution: {e}")
    finally:
        # Clean up temporary files
        if os.path.exists(temp_source_file_path):
            os.remove(temp_source_file_path)
        if os.path.exists(temp_output_file_path):
            os.remove(temp_output_file_path)

#The package is just already installed, so we just need to import it

def main():
    # Example BrainFuck code to print "Hello World!"
    brainfuck_code = """
    ++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.
    """
    run_brainfuck_code(brainfuck_code)
if __name__ == "__main__":
    main()