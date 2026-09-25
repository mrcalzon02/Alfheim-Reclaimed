# Tomb Architecture — giving the Elder Kings a programme instead of a floor plan

**Role:** authoritative design record for the funerary half of the Deepworks.
**Status:** `composition and articulated-excavation rebuild implemented 2026-09-12; latest shape pass runtime pending`.
**Authority:** subordinate to `INSTRUCTIONS.md` and `DEEPWORKS.md`. Governs
`tomb_centre`/`tomb_approach`/`tomb_wing`/`tomb_gallery` in `tools/gen_deep_archaeology.py` and the seventeen
blocks of `tools/funerary_set_manifest.json`.
**Owner direction, 2026-09-12:** *"They read as messy disorganized and impromptu … there should
be distinctive pass at producing recognizable royal tombs, crypts and mausoleum structures at the
massive scale I asked for and not burying the detail under a smattering of random blocks as
appears to have been done with our existing set up. We can use Egyptian tombs and Celtic
mausoleums as our inspirations for structuring and layout dense expansive richly adorned tombs."*

---

## 1. The scale is not the problem

Four tomb templates — centre 47x22x47, approach 17x18x33, royal wing 47x22x47 and dynastic gallery
47x22x47 — assemble into a thirteen-piece pinwheel roughly 207 blocks across. The vocabulary is
there too, and it was expensive: pointed arches on both axes, alcoves,
cornice runs, a gantry triforium, stair flights, scaled grave-door bays, and seventeen bespoke
funerary blocks with their own models and textures.

**Nothing below asks for more geometry or more blocks.** The complaint is composition, and the
diagnosis is that there is none.

## 2. Why it reads as impromptu — six findings, all from the source

**2.1 Every room is the same room.** `tomb_wing` declares three rectangles —
`(5,5,19,20)`, `(27,5,41,20)`, `(14,25,32,41)` — and runs one identical loop over all three:
hollow, clear, quartz plinth, one light at the centre, gantry, one stair flight, arches at a
6-block pitch, cornice. No room is *for* anything. A royal tomb is a sequence of differently
purposed spaces; this is one space repeated three times.

**2.2 The funerary set is placed by four unrelated coordinate lists.** In that same function:
sarcophagi at `(12,10) (34,10) (23,31)`, tapestries at `(12,19) (34,19) (23,40)`, carvings at
`(6,12) (40,12) (15,33)`, statues at `(8,9) (30,9) (18,29)`. Take burial one: its sarcophagus sits
at z=10, its tapestry nine blocks away at the room's far edge, its statue in a corner, its carving
on a side wall. **The four elements of one grave are never composed around it.** Nothing is
centred, nothing faces the burial, and no motif repeats at an interval the eye can find.

**2.3 There is a literal scatter of loose blocks.** Sixteen `alfheim:tomb_debris` placements at
hand-written coordinates — ten in the wing, six in the centre — bearing no relation to a doorway, a
breach or a burial. This is the "smattering of random blocks", exactly.

**2.4 The residue outnumbered the ornament about forty to one.** Measured before today's change,
the wing carried 644 ingress, 364 debris and 158 wear blocks — 10.9% detail over **forty block
ids** — against roughly forty blocks of actual funerary content. A single memorial carving cannot
read as an ornament inside that. It reads as one more speckle.

**2.5 The tomb was wetter and rootier than the mine still being dug.** `DETAIL_TUNING` had the
tomb at `roots=0.10` against the quarry's `0.09`, and `seep="damp", seep_rate=0.10`, in a chamber
whose whole architectural purpose is to stay dry and shut. The generator's own comment says *"a
quarry was worked, a tomb was sealed and a faultwork failed, so they do not get the same
residue"* — and then gave them nearly the same residue.

**2.6 The plan fights the funerary axis.** `four_doors(p, 3, 3, 7)`, a cross of corridors through
the centre, and four identical grave-door bays on all four sides. Four equal entrances make a
crossroads. A tomb has **one** way in, and the whole point of an approach is that it ends.

There is also a decorative lattice — three concentric wall rectangles with gaps at `%9` and `%11`
— which produces an unreadable moiré of stubs rather than a colonnade. It is pattern used as
texture where architecture needed rhythm.

## 3. What the two named inspirations actually supply

Both give the same three things the build is missing: a **sequence**, a **single axis**, and
**ornament concentrated where the eye already is** rather than spread evenly.

| | Egyptian royal tomb (KV type) | Celtic passage grave / mausoleum |
|---|---|---|
| approach | one descending corridor, narrowing | one long low passage, aligned so light reaches the chamber once a year |
| barrier | sealed and plastered doorways; a well shaft as a false floor | kerbstone ring; a threshold stone carved across the entry |
| middle | antechamber, then a pillared hall | the passage itself, lengthening and lowering |
| centre | burial chamber, sarcophagus sunk below the floor | round chamber under a corbelled beehive vault |
| annexes | treasury and annexe off the chamber; a serdab looking in | three cruciform recesses off the round chamber |
| ornament | register bands of relief covering whole walls, continuously | spirals and lozenges concentrated on kerb and lintel |

Two readings of one idea, and they disagree usefully: Egyptian ornament is **continuous surface**,
Celtic ornament is **concentrated at the threshold**. The pack has room for both, because it has
two stone families and two spines — Court stone for the register walls, carved thresholds where a
passage changes.

## 4. The architecture

### 4.1 A room is a role, not a rectangle

```
room := { role, extent, axis, furniture[], threshold{} }
```

Nine roles, each with its own builder and its own furniture rule, replacing the one loop:

| role | what only it does |
|---|---|
| `descent` | the single entrance; floor drops, ceiling drops with it, walls narrow |
| `seal` | a grave-door bay that fills the passage, not one standing beside it |
| `antechamber` | wide, low, register-banded; the only room where offerings accumulate |
| `hall_of_names` | pillared; carvings in a continuous band at one height, not two scattered blocks |
| `burial` | sarcophagus sunk below floor level on the room axis, statues flanking and facing it, tapestry on the wall behind |
| `treasury` | the only room with a chest; small, off the burial, one door |
| `serdab` | sealed, no door, a statue and a slit looking into the burial |
| `dynastic_cloister` | a columned monastic crypt with four family lines across four generations |
| `treasure_vault` | a sealed terminal hoard where gold and mana-metals become architectural masses |

**Furniture is placed relative to the room, never at an absolute coordinate.** That single change
is most of what "recognizable" means: it is the difference between a grave and four objects that
happen to be nearby.

### 4.2 One axis, and it ends

The cross plan and `four_doors` go. The complex reads `descent -> seal -> antechamber ->
hall_of_names -> burial`, with `treasury` and `serdab` hung off the burial, and the wings carrying
further `burial`/`antechamber` pairs. The jigsaw already chains nine pieces; what changes is that
the pieces stop being interchangeable.

### 4.3 Ornament is a band, not a probability

A register band is a *run* of carved and polished courses at one height along a whole wall, its
motif repeating at a fixed interval. It is generated by the same helper family that already draws
`cornice_rect`, at a lower height and with funerary blocks in the course. This is how the seventeen
bespoke blocks stop competing with the residue: they appear **in formation**, and formation is what
the eye reads as intent.

### 4.4 Debris is evidence, not texture

`tomb_debris` stays — `check_deep_archaeology_runtime.py` requires it in the palette, and a
broken-into tomb should show it. It moves to where the tomb was broken into: at the seal, in the
breach, and trailing from it. Sixteen blocks placed by a rule about a robbery, not sixteen
coordinates.

## 5. What must not become possible

1. **No room without a role.** Every enclosed space belongs to one of the seven; a bare rectangle
   is a bug.
2. **No furniture at an absolute coordinate.** Every funerary block is placed relative to the room
   that owns it, so a room that moves takes its grave with it.
3. **No second entrance.** Exactly one `descent` per complex, and the axis from it to the burial is
   unbroken.
4. **Residue never exceeds ornament in a burial room.** Counted per room, not per piece — the
   per-piece average is precisely what hid this.
5. **No new blocks.** The seventeen exist and the 42 stones exist. This is a composition pass.

Each wants a guard in `check_deep_archaeology.py` before the rebuild ships. Today's checks count
blocks and palettes, and would pass all five violations.

## 6. Staging

| stage | delivers | acceptance |
|---|---|---|
| **1** *(done 2026-09-12)* | residue budget corrected for a sealed tomb | wing residue 1,166 -> 340 blocks; detail 10.9% -> 8.0%, still clear of the 4% floor; all four checkers clean |
| **2** *(done 2026-09-12)* | the room-role registry and relative furniture placement | the burial composition is derived from one `TombRoom` extent; output validation confines every funerary object to its owning room |
| **3** *(done 2026-09-12)* | the single axis: `descent`/`seal` replace `four_doors` and the corridor cross | the Hall of Names has one open processional entrance and three sealed dynastic branches |
| **4** *(done 2026-09-12)* | register bands; the `%9`/`%11` lattice removed | continuous fixed-interval carving courses now outweigh all residue inside the burial room |
| **5** *(geometry done 2026-09-12)* | `treasury` and `serdab`; debris re-placed as breach evidence | the treasury has one doorway, the serdab is sealed behind a sight-slit, and all four debris blocks trail from the forced wing seal; runtime walk remains |

Stage 2 is the one that changes the reading. Stages 3 to 5 are what make it a tomb rather than a
well-furnished cellar.

### 6.1 Implemented composition

The rebuilt complex leads with an Egyptian processional grammar and uses Celtic massing as its
accent. The centre is now a long, double-colonnaded Hall of Names rather than a cross-shaped hub.
Its north mouth is the sole open entrance; the other three attached dynastic branches begin behind
full grave-door bays. Each approach compresses into a stepped descent and opens through a broad,
register-banded antechamber.

Each repeated wing is one king's precinct, not three copies of a generic room: a stepped-octagonal
axial burial hall under a corbelled crown, a one-door offering treasury, and a sealed serdab whose
guardian looks into the chamber through a narrow wall opening. The sarcophagus, paired guardians,
rear tapestry, continuous memorial register and breach trail are all calculated from that burial
room's extent. There is no remaining `%9`/`%11` wall lattice and no hand-scattered tomb debris.

The checker now treats this programme as a contract. It asserts the nine roles, confines all
funerary objects to registered rooms, requires three centre seals plus one open entrance, requires
the debris trail to remain at the forced threshold, verifies the serdab stays closed, and compares
ornament with residue inside the burial room rather than across an entire template.

### 6.2 Necropolis expansion

The royal precinct is no longer the end of a branch. Each of the four wings turns sideways into a
47-block dynastic generation crypt, taking the assembled complex from nine pieces to thirteen
without turning the whole plan into an impossibly long cross. The four terminal galleries contain four
parallel family lines across four generations: sixteen raised three-module sarcophagi per gallery,
sixty-four ancestral burials plus the four sovereign graves.

Each ancestor rests on a raised smooth-quartz dais with a carved head plinth and stair apron. Two
quartz colonnades define a central monastic nave; repeated pointed ribs, continuous memorial
registers, upper cloister walks and opposed stair flights give the gallery a vertical order. A
sealed hoard terminates the axis behind another grave-door bay. Its stepped deposits use gold,
Manasteel, Elementium, mana diamond, Dragonstone and one Terrasteel crown, with two supplementary
coffers drawing from a dedicated dynastic treasure table. Wealth is concentrated in this room and
composed as plinths and masses, not randomly sprinkled through circulation space.

### 6.3 Articulated excavation — the template is not the room

The 47x47 dimensions are editing envelopes, not masonry footprints. The generic full-envelope
shell has been removed from all four tomb pieces:

- The Hall of Names is a high north/south barrel-vaulted nave crossed by a lower sealed transept,
  with its treasury projecting from one side. Its four corners remain native rock.
- The approach is three overlapping tubes of different width, height and floor level. It expands
  by stages into the antechamber instead of maintaining one rectangular section.
- The royal precinct is a true stepped octagonal rotunda with an eight-sided corbel crown. Its
  upper ambulatory follows the facets; the treasury, serdab, entrance neck and gallery passage
  project independently from the central mass.
- The generation crypt is a narrow axial nave crossed by four separated burial transepts. Rock
  remains between the transepts, so sixteen graves occupy recognizable family chapels rather than
  one square hall.

This is now checked from the generated foundations. No tomb template may occupy a complete row of
its bounding box, exceed 70% of its envelope, or collapse to fewer than three distinct row widths.
The current footprints occupy only 44–63% of their envelopes.

## 7. Open decisions — owner's call, not assumptions

1. **Which inspiration leads?** Egyptian continuous register walls and Celtic threshold
   concentration are both supported. Leading with one and accenting with the other reads stronger
   than an even mix, and the choice sets the stone budget.
2. **How strongly should the burial crown dominate?** The royal chamber now has a five-course
   octagonal corbel crown; a client walk should decide whether it needs a taller apex.
3. **One royal tomb, or a family?** The roster also carries `kings_cliff_tomb`, `grey_barrow`,
   `capfall_barrow` and `rotwood_barrow`. The room grammar would serve all five; whether the
   barrows become small tombs or stay barrows is a campaign question.
4. **Is the serdab worth a sealed room a player cannot enter?** It is the most authentic element
   here and also the one nobody will see from inside.
5. **How much larger?** Resolved by the necropolis expansion: thirteen dense pieces within a
   roughly 207-block pinwheel, with four terminal generation crypts rather than increasing any one
   room's empty span. A straight 301-block version was rejected at runtime because Minecraft 1.20.1
   caps `max_distance_from_center` at 128; folding the galleries sideways preserves all content.
