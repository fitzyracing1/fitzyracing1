# Bitmap CPU Starter

This workspace is a clean starting place for a CPU project where a 1-bit BMP image becomes the CPU's initial memory.

## What it does

- Loads an uncompressed 1-bit BMP file
- Flattens the image into row-major bits
- Stores those bits as CPU memory
- Resets the program counter to `0`, so the bitmap becomes the CPU's new starting state

## Files

- `bitmap_cpu/bmp_loader.py`: reads a 1-bit BMP without extra dependencies
- `bitmap_cpu/cpu.py`: tiny CPU model backed by bitmap memory
- `main.py`: command-line entry point

## Run it

```powershell
python main.py .\processor.bmp --steps 16
```

Expected output looks like this:

```text
Loaded 8x8 bitmap into CPU memory.
Memory image:
01010101
11110000
...
```

## Notes

- This starter currently supports standard uncompressed 1-bit BMP files only.
- Pixel rows are normalized so the top row of the image becomes the first row in CPU memory.
- A `1` bit in the bitmap stays `1` in memory, and a `0` stays `0`.

## Next ideas

- Add an instruction decoder so groups of bits become opcodes
- Map sections of the bitmap into ROM, RAM, registers, or microcode
- Support saving the CPU memory image back out to a BMP for debugging
