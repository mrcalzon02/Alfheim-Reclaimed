#!/usr/bin/env python3
"""Validate the authored five-Act bestiary; a pass does NOT mean mobs are implemented."""
import json
from collections import Counter
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "alfheim_reclaimed_design/monastery_labyrinth/monster_catalog.json"

def main():
    data=json.loads(CATALOG.read_text(encoding="utf-8"))
    creatures=data["creatures"]
    ids=[e["id"] for e in creatures]
    assert len(creatures)==130, f"expected 130 species, got {len(creatures)}"
    assert len(set(ids))==len(ids), "duplicate creature id"
    assert set(e["act"] for e in creatures)=={1,2,3,4,5}
    counts=Counter(e["act"] for e in creatures)
    bosses=Counter(e["act"] for e in creatures if e["role"]=="boss")
    assert all(counts[act]==26 and bosses[act]==1 for act in range(1,6))
    assert len(set(e["primary"]["id"] for e in creatures))==len(creatures)
    assert all(e["implementation"]=="design_only" and e["model"]=="unassigned" for e in creatures)
    assert all(e["primary"]["description"] and e["counterplay"] for e in creatures)
    assert len(set(e["role"] for e in creatures))>=10
    assert len(data["affixes"])>=30
    assert len(set(a["id"] for a in data["affixes"]))==len(data["affixes"])
    assert all(e["spawning"]["no_depth_multiplier"] and
               e["spawning"]["mob_level_source"]=="mine_and_slash_distance_from_spawn_only"
               for e in data["encounters"])
    print(f"Five-Act bestiary design OK: {len(creatures)} authored species, "
          f"{sum(bosses.values())} bosses, {len(data['affixes'])} affixes; runtime NOT implemented")
if __name__=="__main__":
    main()
