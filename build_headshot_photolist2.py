import os
import json
from PIL import Image
import colorsys

# Folder containing your headshot JPEGs/PNGs
HEADSHOT_DIR = "headshotimages"
OUTPUT_JSON = "photolist2.json"

def compute_average_hsl(img):
  # downscale for speed
  target_w = 32
  aspect = img.height / img.width
  target_h = max(8, int(target_w * aspect))

  small = img.resize((target_w, target_h), Image.LANCZOS).convert("RGB")
  pixels = list(small.getdata())

  r_sum = g_sum = b_sum = 0
  for r, g, b in pixels:
    r_sum += r
    g_sum += g
    b_sum += b

  count = len(pixels)
  r_avg = r_sum / count / 255
  g_avg = g_sum / count / 255
  b_avg = b_sum / count / 255

  h, l, s = colorsys.rgb_to_hls(r_avg, g_avg, b_avg)
  return {"h": h, "s": s, "l": l}

def main():
  files = sorted(os.listdir(HEADSHOT_DIR))
  out = []

  for filename in files:
    if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
      continue

    path = os.path.join(HEADSHOT_DIR, filename)
    print("Processing", filename)
    try:
      img = Image.open(path)
      hsl = compute_average_hsl(img)
      out.append({
        "name": filename,
        "h": hsl["h"],
        "s": hsl["s"],
        "l": hsl["l"]
      })
    except Exception as e:
      print("  ⚠️ error, skipping:", e)

  with open(OUTPUT_JSON, "w") as f:
    json.dump(out, f, indent=2)

  print(f"\nDone. Wrote {len(out)} entries to {OUTPUT_JSON}")

if __name__ == "__main__":
  main()
