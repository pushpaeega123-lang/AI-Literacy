import subprocess
import os

files = [
    ("static/js", "keyboard.js"),
    ("static/js", "main.js"),
    ("static/js", "mascot.js"),
    ("static/js", "tracing.js"),
    ("static/js", "voice_eval.js"),
    ("static/js", "notifications.js"),
    ("static", "sw.js")
]
for folder, f in files:
    filepath = os.path.join(folder, f)
    result = subprocess.run(["node", "--check", filepath], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"SUCCESS: {f} syntax is valid!")
    else:
        print(f"ERROR in {f}:")
        print(result.stderr)
