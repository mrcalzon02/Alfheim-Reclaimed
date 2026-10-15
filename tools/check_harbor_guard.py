"""Prevent a stale Java footprint or runtime artifact from bypassing shore policy."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
layout=json.loads((ROOT/'tools/harbor_complex_layout.json').read_text(encoding='utf-8'))['layout']
java=(ROOT/'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/worldgen/HarborGeometry.java').read_text(encoding='utf-8')
rows=re.findall(r'new Part\("([^"]+)",\s*(-?\d+),\s*(-?\d+),\s*(\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)\)',java)
actual=[(r[0],*map(int,r[1:])) for r in rows]
expected=[(n['name'],n['origin'][0],n['origin'][2],n['rotation'],n['bounds'][0],n['bounds'][2],n['bounds'][3],n['bounds'][5]) for n in layout]
assert actual==expected,(actual,expected)
settings=json.loads((ROOT/'kubejs/data/alfheim/worldgen/structure/harbor_complex.json').read_text())
assert settings['type']=='alfheim_companion:shoreline_harbor' and settings['terrain_adaptation']=='none'
placement=json.loads((ROOT/'kubejs/data/alfheim/worldgen/structure_set/harbor_complex.json').read_text(encoding='utf-8'))['placement']
from district_policy import PLACEMENT
assert placement==PLACEMENT
policy=(ROOT/'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/worldgen/HarborSite.java').read_text(encoding='utf-8')
assert 'GENERATION_COLUMN_LIMIT=32' in policy and 'GENERATION_TIME_LIMIT=150_000_000L' in policy
report=ET.parse(ROOT/'first_party_mods/alfheim_companion/build/test-results/test/TEST-com.continuityworks.alfheimcompanion.worldgen.HarborSiteTest.xml').getroot()
assert report.attrib['failures']==report.attrib['errors']=='0' and int(report.attrib['tests'])==20
placer=(ROOT/'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/worldgen/HarborStructure.java').read_text(encoding='utf-8')
assert 'var site=auditGeneratedBounded(c.chunkGenerator()' in placer,'natural generation must use bounded policy'
from gen_harbor_proposals import source,TARGET
assert TARGET.read_text(encoding='utf-8')==source(),'diagnostic proposal/source mismatch'
build=json.loads((ROOT/'tools/harbor_guard_build.json').read_text())
assert hashlib.sha256((ROOT/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest()==build['installed_sha256']
print('HARBOR GUARD STATIC PASS: bounded natural placement, source-equal footprints, no terrain adjustment, twenty policy tests and installed artifact hash')
