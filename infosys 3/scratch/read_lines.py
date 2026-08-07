import sys

def main():
    filepath = r"c:\Users\user\Downloads\infosys40\infosys 3\app.py"
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    
    start = int(sys.argv[1]) - 1 if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else len(lines)
    
    for idx in range(start, min(end, len(lines))):
        line = lines[idx]
        # Replace non-ascii chars to avoid print encode issues on Windows cmd
        safe_line = line.encode('ascii', errors='replace').decode('ascii')
        print(f"{idx + 1:5d}: {safe_line}", end="")

if __name__ == "__main__":
    main()
