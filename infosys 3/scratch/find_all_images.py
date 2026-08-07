import os

workspace = r"c:\Users\user\Downloads\infosys40"
image_files = []
for root, dirs, files in os.walk(workspace):
    for f in files:
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif')):
            image_files.append(os.path.join(root, f))

print(f"Found {len(image_files)} images:")
for img in image_files:
    print(img)
