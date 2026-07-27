from __future__ import annotations

import argparse

from bitmap_cpu import BitmapBackedCPU


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load a 1-bit BMP and use it as the CPU's starting memory image."
    )
    parser.add_argument("bitmap", help="Path to a 1-bit uncompressed BMP file.")
    parser.add_argument(
        "--steps",
        type=int,
        default=8,
        help="How many bits to read after loading the bitmap.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    cpu = BitmapBackedCPU()
    image = cpu.load_bitmap(args.bitmap)

    print(f"Loaded {image.width}x{image.height} bitmap into CPU memory.")
    print("Memory image:")
    print(cpu.dump_memory())
    print()
    print(f"First {args.steps} bits:")

    bits = []
    for _ in range(min(args.steps, len(cpu.memory))):
        bits.append(str(cpu.step()))
    print(" ".join(bits))


if __name__ == "__main__":
    main()
