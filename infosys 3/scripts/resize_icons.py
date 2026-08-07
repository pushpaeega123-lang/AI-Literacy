import os
import shutil
from PIL import Image

# Path configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_ICON_PATH = r"C:\Users\user\.gemini\antigravity-ide\brain\1c94369d-6ded-46cb-a728-13bf6ac9c688\pwa_icon_base_1785499127442.png"
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "images", "icons")

SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

def generate_icons():
    if not os.path.exists(BASE_ICON_PATH):
        print(f"Base icon not found at {BASE_ICON_PATH}!")
        return

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Target icons directory: {OUTPUT_DIR}")

    # Open base image
    img = Image.open(BASE_ICON_PATH)

    for size in SIZES:
        resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
        out_name = f"icon_{size}.png"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        resized_img.save(out_path, "PNG")
        print(f"Generated icon: {out_name} ({size}x{size})")

    # Also copy 512 icon as favicon or logo
    logo_target = os.path.join(BASE_DIR, "static", "images", "logo.png")
    shutil.copy2(os.path.join(OUTPUT_DIR, "icon_512.png"), logo_target)
    print("Copied icon_512.png to static/images/logo.png")

if __name__ == "__main__":
    generate_icons()
