from __future__ import annotations

from pathlib import Path
import struct
import tempfile
import unittest

from bitmap_cpu import BitmapBackedCPU, load_1bit_bmp


def make_test_bmp(width: int, height: int, rows: list[str]) -> bytes:
    row_width_bytes = ((width + 31) // 32) * 4
    pixel_rows = []

    for row in reversed(rows):
        byte = 0
        bit_count = 0
        packed = bytearray()
        for char in row:
            byte = (byte << 1) | int(char)
            bit_count += 1
            if bit_count == 8:
                packed.append(byte)
                byte = 0
                bit_count = 0

        if bit_count:
            byte <<= 8 - bit_count
            packed.append(byte)

        while len(packed) < row_width_bytes:
            packed.append(0)

        pixel_rows.append(bytes(packed))

    pixel_data = b"".join(pixel_rows)
    file_size = 14 + 40 + 8 + len(pixel_data)
    pixel_offset = 14 + 40 + 8

    file_header = struct.pack("<2sIHHI", b"BM", file_size, 0, 0, pixel_offset)
    info_header = struct.pack(
        "<IIIHHIIIIII",
        40,
        width,
        height,
        1,
        1,
        0,
        len(pixel_data),
        2835,
        2835,
        2,
        0,
    )
    color_table = struct.pack("<II", 0x00000000, 0x00FFFFFF)
    return file_header + info_header + color_table + pixel_data


class BitmapCpuTests(unittest.TestCase):
    def test_load_bitmap_preserves_top_down_rows(self) -> None:
        bmp = make_test_bmp(4, 2, ["1010", "0101"])
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "processor.bmp"
            path.write_bytes(bmp)

            image = load_1bit_bmp(path)

        self.assertEqual(image.width, 4)
        self.assertEqual(image.height, 2)
        self.assertEqual(image.pixels, ((1, 0, 1, 0), (0, 1, 0, 1)))

    def test_cpu_uses_bitmap_as_memory_image(self) -> None:
        bmp = make_test_bmp(4, 2, ["1111", "0001"])
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "processor.bmp"
            path.write_bytes(bmp)

            cpu = BitmapBackedCPU()
            cpu.load_bitmap(path)

        self.assertEqual(cpu.memory, [1, 1, 1, 1, 0, 0, 0, 1])
        self.assertEqual(cpu.program_counter, 0)
        self.assertEqual(cpu.step(), 1)
        self.assertEqual(cpu.program_counter, 1)


if __name__ == "__main__":
    unittest.main()
