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

def install_bf_compiler():
    """Install the bf-compiler if not already installed."""
    if shutil.which("bf") is not None:
        print("bf-compiler is already installed.")
        return
    
    system_platform = platform.system()
    
    if system_platform == "Windows":
        download_and_install_bf_compiler_in_windows()
    elif system_platform in ["Linux", "Darwin"]:  # Darwin is macOS
        download_and_install_bf_compiler_in_unix()
    else:
        print(f"Unsupported platform: {system_platform}")
        sys.exit(1)
    if shutil.which("bf") is None:
        print("Failed to install bf-compiler.")
        sys.exit(1)
    print("bf-compiler installed successfully.")
def download_and_install_bf_compiler_in_windows():
    """Download and install bf-compiler in Windows."""
    try:
        bf_url = "https://github.com/LinnerFeng/HesterIDE/release/download/v1.0.0/bf-windows.zip"
        download_path = "bf-windows.zip"
        urllib.request.urlretrieve(bf_url, download_path)
        print("bf-compiler downloaded successfully. Installing...")
        shutil.unpack_archive(download_path, "bf-compiler")
        bf_executable_path = os.path.join("bf-compiler", "bf.exe")
        target_path = os.path.join(os.getenv("ProgramFiles"), "bf")
        os.makedirs(target_path, exist_ok=True)
        shutil.move(bf_executable_path, os.path.join(target_path, "bf.exe"))
        os.environ["PATH"] += os.pathsep + target_path
        print("bf-compiler installed successfully.")
    except Exception as e:
        bf_url="https://sourceforge.net/projects/bf-compiler/files/latest/download"
        download_path = "bf-windows-installer.exe"
        try:
            urllib.request.urlretrieve(bf_url, download_path)
            print("bf-compiler downloaded successfully. Installing...")
            subprocess.run([download_path, '/VERYSILENT', '/NORESTART'], check=True)
            print("bf-compiler installed successfully.")
        except Exception as e:
            print(f"Failed to download or install bf-compiler: {e}")
            sys.exit(1)
    finally:
        if os.path.exists(download_path):
            os.remove(download_path)
def download_and_install_bf_compiler_in_unix():
    """Download and install bf-compiler in Linux or macOS."""
    try:
        bf_url = "https://github.com/LinnerFeng/HesterIDE/release/download/v1.0.0/bf-unix.tar.gz"
        download_path = "bf-unix.tar.gz"
        urllib.request.urlretrieve(bf_url, download_path)
        print("bf-compiler downloaded successfully. Installing...")
        shutil.unpack_archive(download_path, "bf-compiler")
        bf_executable_path = os.path.join("bf-compiler", "bf")
        target_path = "/usr/local/bin/bf"
        shutil.move(bf_executable_path, target_path)
        os.chmod(target_path, os.stat(target_path).st_mode | stat.S_IEXEC)
        print("bf-compiler installed successfully.")
    except Exception as e:
        bf_url="https://sourceforge.net/projects/bf-compiler/files/latest/download"
        download_path = "bf-windows-installer.exe"
        try:
            urllib.request.urlretrieve(bf_url, download_path)
            print("bf-compiler downloaded successfully. Installing...")
            subprocess.run([download_path, '/VERYSILENT', '/NORESTART'], check=True)
            print("bf-compiler installed successfully.")
        except Exception as e:
            print(f"Failed to download or install bf-compiler: {e}")
            sys.exit(1)
    finally:
        if os.path.exists(download_path):
            os.remove(download_path)

def main():
    install_bf_compiler()
    # Example BrainFuck code to print "Hello World!"
    brainfuck_code = """
    ++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.
    """
    run_brainfuck_code(brainfuck_code)
if __name__ == "__main__":
    main()