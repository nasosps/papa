from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


INPUT = Path("logo.png")
OUTPUT_BW = Path("logo_3dprint_2x_bw.png")
OUTPUT_INVERTED = Path("logo_3dprint_2x_inverted.png")

# Tuned for this specific logo so the strokes read closer to "double thickness"
# after raster dilation, while still preserving the inner details.
THRESHOLD = 235
DILATION_SIZE = 41
PADDING = 24


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(value, high))


def main() -> None:
    image = Image.open(INPUT).convert("L")

    # Convert to a hard black/white mask first so the result stays printable.
    binary = image.point(lambda p: 0 if p < THRESHOLD else 255, mode="L")

    # Black strokes are dilated by inverting, expanding the white area,
    # then inverting back.
    inverted = ImageOps.invert(binary)
    thickened = ImageOps.invert(inverted.filter(ImageFilter.MaxFilter(size=DILATION_SIZE)))

    bbox = thickened.point(lambda p: 255 if p == 0 else 0, mode="L").getbbox()
    if bbox:
        left, top, right, bottom = bbox
        left = clamp(left - PADDING, 0, thickened.width)
        top = clamp(top - PADDING, 0, thickened.height)
        right = clamp(right + PADDING, 0, thickened.width)
        bottom = clamp(bottom + PADDING, 0, thickened.height)
        thickened = thickened.crop((left, top, right, bottom))

    thickened.save(OUTPUT_BW)
    ImageOps.invert(thickened).save(OUTPUT_INVERTED)

    print(f"Saved {OUTPUT_BW} -> {thickened.size}")
    print(f"Saved {OUTPUT_INVERTED} -> {thickened.size}")


if __name__ == "__main__":
    main()
