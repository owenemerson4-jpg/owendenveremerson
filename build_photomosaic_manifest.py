import os
import json
from PIL import Image
import colorsys

# ------------------------------------------------------------
# CONFIG — You can adjust these paths if needed
# ------------------------------------------------------------
FULL_DIR  = "websitephotos/full"
THUMB_DIR = "websitephotos/thumbs"
OUTPUT_JSON = "photolist.json"

THUMB_WIDTH = 500   # Thumbnail width (height auto-adjusted)


# ------------------------------------------------------------
# Ensure output directories exist
# ------------------------------------------------------------
os.makedirs(THUMB_DIR, exist_ok=True)


# ------------------------------------------------------------
# Utility: Compute average H, S, L of an image
# ------------------------------------------------------------
def compute_average_hsl(img):
    # Downscale heavily for speed & uniformity
    target_w = 32
    aspect = img.height / img.width
    target_h = max(8, int(target_w * aspect))

    small = img.resize((target_w, target_h), Image.LANCZOS).convert("RGB")
    pixels = list(small.getdata())

    # Accumulate RGB values
    r_sum = g_sum = b_sum = 0
    for r, g, b in pixels:
        r_sum += r
        g_sum += g
        b_sum += b

    count = len(pixels)
    r_avg = r_sum / count / 255
    g_avg = g_sum / count / 255
    b_avg = b_sum / count / 255

    # Convert to HSL using Python's colorsys
    h, l, s = colorsys.rgb_to_hls(r_avg, g_avg, b_avg)
    # colorsys returns HLS; convert to HSL
    return {
        "h": h,
        "s": s,
        "l": l
    }


# ------------------------------------------------------------
# Utility: Generate thumbnail
# ------------------------------------------------------------
def create_thumbnail(src_path, dest_path):
    img = Image.open(src_path)
    w, h = img.size

    # Compute scale factor
    scale = THUMB_WIDTH / w
    new_size = (THUMB_WIDTH, int(h * scale))

    img_thumb = img.resize(new_size, Image.LANCZOS)
    img_thumb.save(dest_path, quality=85, optimize=True)


# ------------------------------------------------------------
# Main logic
# ------------------------------------------------------------
def main():
    print("Scanning:", FULL_DIR)
    files = sorted(os.listdir(FULL_DIR))

    output_list = []

    for filename in files:
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        full_path = os.path.join(FULL_DIR, filename)
        thumb_path = os.path.join(THUMB_DIR, filename)

        print(f"Processing: {filename}")

        try:
            img = Image.open(full_path)

            # 1. Compute HSL
            hsl = compute_average_hsl(img)

            # 2. Create thumbnail (only once)
            if not os.path.exists(thumb_path):
                create_thumbnail(full_path, thumb_path)

            # 3. Add record to manifest
            output_list.append({
                "name": filename,
                "h": hsl["h"],
                "s": hsl["s"],
                "l": hsl["l"]
            })

        except Exception as e:
            print("⚠️ Error processing", filename, "→", e)

    # 4. Write JSON manifest
    with open(OUTPUT_JSON, "w") as f:
        json.dump(output_list, f, indent=2)

    print("\nDone! Wrote:", OUTPUT_JSON)
    print(f"Total images processed: {len(output_list)}")


# ------------------------------------------------------------
# Entry
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
