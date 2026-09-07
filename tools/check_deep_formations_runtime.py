"""Audit naturally generated Deepworks formation evidence in a dedicated-server world."""
import argparse
import collections
import gzip
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbt  # noqa: E402


ELEMENTS = {"fire", "water", "earth", "air", "shadow", "light"}


def chunks(region):
    data = region.read_bytes()
    for slot in range(1024):
        location = struct.unpack_from(">I", data, slot * 4)[0]
        sector = location >> 8
        if not sector:
            continue
        start = sector * 4096
        length = struct.unpack_from(">I", data, start)[0]
        compression = data[start + 4]
        payload = data[start + 5:start + 4 + length]
        if compression == 1:
            payload = gzip.decompress(payload)
        elif compression == 2:
            payload = zlib.decompress(payload)
        elif compression != 3:
            raise ValueError(f"{region}: unknown chunk compression {compression}")
        reader = nbt._Reader(payload)
        reader.u1()
        reader.string()
        yield reader.payload(nbt.TAG_COMPOUND)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("world", type=Path)
    args = parser.parse_args()
    region_dir = args.world / "dimensions/mythicbotany/alfheim/region"
    assert region_dir.is_dir(), region_dir
    section_hits = collections.Counter()
    chunk_count = 0
    for region in region_dir.glob("*.mca"):
        for chunk in chunks(region):
            chunk_count += 1
            sections = chunk.get("sections", chunk.get("Level", {}).get("Sections", []))
            for section in sections:
                palette = section.get("block_states", {}).get("palette", [])
                names = {entry["Name"] for entry in palette}
                for element in ELEMENTS:
                    if f"alfheim:mana_glass_{element}" in names:
                        section_hits[element] += 1
    present = {element for element, count in section_hits.items() if count}
    assert chunk_count >= 100, f"only {chunk_count} chunks; not a meaningful fresh-world sample"
    assert len(present) >= 3, f"only {sorted(present)} mana-glass alignments generated"
    print(f"PASS: {chunk_count} Alfheim chunks; natural formation mana-glass in "
          f"{len(present)} alignments: " + ", ".join(f"{e}={section_hits[e]} sections" for e in sorted(present)))


if __name__ == "__main__":
    main()
