from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct


@dataclass(frozen=True)
class BitmapImage:
    width: int
    height: int
    pixels: tuple[tuple[int, ...], ...]

    def flatten_bits(self) -> list[int]:
        return [bit for row in self.pixels for bit in row]


def load_1bit_bmp(path: str | Path) -> BitmapImage:
    data = Path(path).read_bytes()
    if len(data) < 54:
        raise ValueError("File is too small to be a valid BMP.")

    signature = data[:2]
    if signature != b"BM":
        raise ValueError("Only BMP files with the BM signature are supported.")

    pixel_offset = struct.unpack_from("<I", data, 10)[0]
    header_size = struct.unpack_from("<I", data, 14)[0]
    if header_size < 40:
        raise ValueError("Only BITMAPINFOHEADER-style BMP files are supported.")

    width = struct.unpack_from("<i", data, 18)[0]
    height = struct.unpack_from("<i", data, 22)[0]
    planes = struct.unpack_from("<H", data, 26)[0]
    bits_per_pixel = struct.unpack_from("<H", data, 28)[0]
    compression = struct.unpack_from("<I", data, 30)[0]

    if planes != 1:
        raise ValueError("BMP plane count must be 1.")
    if bits_per_pixel != 1:
        raise ValueError("Only 1-bit BMP images are supported.")
    if compression != 0:
        raise ValueError("Compressed BMP images are not supported.")
    if width <= 0 or height == 0:
        raise ValueError("BMP dimensions must be non-zero.")

    row_width_bytes = ((abs(width) + 31) // 32) * 4
    rows: list[tuple[int, ...]] = []

    is_top_down = height < 0
    image_height = abs(height)

    for row_index in range(image_height):
        source_row = row_index if is_top_down else image_height - 1 - row_index
        row_start = pixel_offset + source_row * row_width_bytes
        row_end = row_start + row_width_bytes
        if row_end > len(data):
            raise ValueError("BMP pixel data is truncated.")

        row_data = data[row_start:row_end]
        bits: list[int] = []
        for byte in row_data:
            for bit_index in range(7, -1, -1):
                bits.append((byte >> bit_index) & 1)
                if len(bits) == width:
                    break
            if len(bits) == width:
                break

        rows.append(tuple(bits))

    return BitmapImage(width=width, height=image_height, pixels=tuple(rows))
