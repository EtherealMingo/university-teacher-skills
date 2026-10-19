"""Trim transparent padding from a PNG to its visible content's bounding box.

Usage:
    trim-padding-from-image.py <png-path> [<png-path> ...]

Each argument must be an explicit path to a .png file. The script overwrites
the file in place. The script does NOT walk any directory — passing zero
arguments is an error, not a request to batch-process docs/img/mascot/.

This explicit-argument design exists because the previous version silently
ignored sys.argv and walked docs/img/mascot/, which was a footgun: the
documented invocation pattern looked like it processed a single named file
but actually overwrote every PNG in the mascot directory.
"""
import sys
from pathlib import Path
from PIL import Image

THRESH = 10   # alpha <= 10 treated as padding
PADDING = 4   # px buffer preserved after crop


def trim(path: Path) -> None:
    img = Image.open(path).convert('RGBA')
    alpha = img.getchannel('A')
    px = alpha.load()
    w, h = img.size
    min_x, max_x, min_y, max_y = w, -1, h, -1
    for y in range(h):
        for x in range(w):
            if px[x, y] > THRESH:
                min_x = min(min_x, x); max_x = max(max_x, x)
                min_y = min(min_y, y); max_y = max(max_y, y)
    if max_x == -1:
        print(f'skip {path.name}: image is fully transparent')
        return
    bbox = (max(min_x - PADDING, 0), max(min_y - PADDING, 0),
            min(max_x + PADDING, w - 1) + 1, min(max_y + PADDING, h - 1) + 1)
    cropped = img.crop(bbox)
    if cropped.size != img.size:
        cropped.save(path)
        print(f'cropped {path.name}: {img.size} -> {cropped.size}')
    else:
        print(f'unchanged {path.name}: already tight ({img.size})')


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        sys.stderr.write(
            "usage: trim-padding-from-image.py <png-path> [<png-path> ...]\n"
            "Each argument must be an explicit path to a .png file.\n"
        )
        return 2
    rc = 0
    for arg in argv[1:]:
        path = Path(arg)
        if not path.is_file():
            print(f'skip {arg}: not a file')
            rc = 1
            continue
        if path.suffix.lower() != '.png':
            print(f'skip {arg}: not a .png')
            rc = 1
            continue
        trim(path)
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv))
