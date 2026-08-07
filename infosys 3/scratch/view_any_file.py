import sys

def main():
    filepath = sys.argv[1]
    start = int(sys.argv[2]) - 1 if len(sys.argv) > 2 else 0
    end = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
        
    end = end if end is not None else len(lines)
    for idx in range(start, min(end, len(lines))):
        line = lines[idx]
        safe_line = line.encode('ascii', errors='replace').decode('ascii')
        print(f"{idx + 1:5d}: {safe_line}", end="")

if __name__ == "__main__":
    main()
