import os
import json
from PIL import Image
import colorsys

FULL_DIR = "headshotimages/full"
THUMB_DIR = "headshotimages/thumbs"
OUTPUT_JSON = "photolist2.json"

THUMB_WIDTH = 500   # target width for thumbnails

os.makedirs(THUMB_DIR, exist_ok=True)

def compute_average_hsl(img):
    # downscale for sampling
    target_w = 32
    aspect = img.height / img.width
    target_h = max(8, int(target_w * aspect))

    small = img.resize((target_w, target_h), Image.LANCZOS).convert("RGB")
    pixels = list(small.getdata())

    r = g = b = 0
    for pr, pg, pb in pixels:
        r += pr
        g += pg
        b += pb

    count = len(pixels)
    r /= count * 255
    g /= count * 255
    b /= count * 255

    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return {"h": h, "s": s, "l": l}

def make_thumbnail(src_path, dst_path):
    img = Image.open(src_path).convert("RGB")

    w, h = img.size
    new_h = int(h * (THUMB_WIDTH / w))
    thumb = img.resize((THUMB_WIDTH, new_h), Image.LANCZOS)

    thumb.save(dst_path, quality=88, optimize=True)

def main():
    output = []

    for filename in sorted(os.listdir(FULL_DIR)):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue

        full_path = os.path.join(FULL_DIR, filename)
        thumb_path = os.path.join(THUMB_DIR, filename)

        print("Processing:", filename)

        try:
            # Generate thumbnail
            make_thumbnail(full_path, thumb_path)

            # Load thumbnail for HSL
            img = Image.open(thumb_path)
            hsl = compute_average_hsl(img)

            output.append({
                "name": filename,
                "h": hsl["h"],
                "s": hsl["s"],
                "l": hsl["l"]
            })

        except Exception as e:
            print("  ⚠️ Error:", e)

    with open(OUTPUT_JSON, "w") as f:
        json.dump(output, f, indent=2)

    print("\nDone! Wrote thumbnails +", len(output), "entries to photolist2.json")

if __name__ == "__main__":
    main()
