# Elven late-game barter — 2026-10-16

Right-click an adult Elven Citizen to open Minecraft's standard villager trading
screen. Each social role has six offers; all four appearances of a role share
that role's catalogue. The twelve roles provide 72 offers across ingredients,
components and worked intermediate products.

Both payment slots are consumed. Payments require a finished material from
Ember Tempering, Rime Lattice Binding, Gravegilt Binding or Crown Weaving, plus
an Ars Nouveau Source reagent. Intermediate products require the finished
material from their own chain, so ordinary currency cannot unlock an unfinished
chain. No finished ladder material, unfinished sequenced assembly, equipment or
quest unlock is sold. No existing crafting recipe was removed or changed.

Offers have 2–8 uses. Stock refills after 24,000 game ticks (20 minutes of
active server time at normal tick rate), while the citizen is not trading.
Sleeping and changing the time of day do not speed this up. Unloaded citizens
catch up when loaded. Offers, stock usage and the restock timestamp persist
across saving; appearance and entity identity remain compatible with the prior
citizens. There is no villager-level grind, price discount system or trade XP.

The catalogue is authored in
`first_party_mods/alfheim_companion/src/main/resources/data/alfheim_companion/elven_trades.json`.
It is packaged in the companion jar and requires rebuilding to change.

## Offers

| Role | First payment | Second payment | Received | Stock |
|---|---|---|---|---:|
| Serf | 1 Emberbound Weave | 2 Earth Essence | 32 Dreamwood | 8 |
| Serf | 1 Emberbound Weave | 2 Earth Essence | 32 Livingrock | 8 |
| Serf | 1 Emberbound Weave | 2 Earth Essence | 16 Mana Powder | 8 |
| Serf | 1 Emberbound Weave | 2 Earth Essence | 8 Elementium Ingot | 8 |
| Serf | 1 Emberbound Weave | 2 Earth Essence | 4 Dragonstone | 8 |
| Serf | 1 Emberbound Weave | 2 Earth Essence | 4 Pixie Dust | 8 |
| Servant | 1 Emberbound Weave | 4 Source Gem | 2 Air Essence | 4 |
| Servant | 1 Emberbound Weave | 4 Source Gem | 2 Earth Essence | 4 |
| Servant | 1 Emberbound Weave | 4 Source Gem | 2 Fire Essence | 4 |
| Servant | 1 Emberbound Weave | 4 Source Gem | 2 Water Essence | 4 |
| Servant | 1 Emberbound Weave | 4 Source Gem | 2 Abjuration Essence | 4 |
| Servant | 1 Emberbound Weave | 4 Source Gem | 2 Conjuration Essence | 4 |
| Steward | 1 Rimebound Lattice | 2 Abjuration Essence | 2 Rune Mana | 4 |
| Steward | 1 Rimebound Lattice | 2 Abjuration Essence | 2 Rune Winter | 4 |
| Steward | 1 Rimebound Lattice | 2 Abjuration Essence | 2 Rune Autumn | 4 |
| Steward | 1 Rimebound Lattice | 2 Abjuration Essence | 2 Rune Spring | 4 |
| Steward | 1 Rimebound Lattice | 2 Abjuration Essence | 2 Rune Summer | 4 |
| Steward | 1 Rimebound Lattice | 2 Abjuration Essence | 8 Pixie Dust | 4 |
| Artisan | 1 Emberbound Weave | 4 Source Gem | 1 Scorched Filament | 4 |
| Artisan | 1 Emberbound Weave | 4 Source Gem | 1 Quenched Thread | 4 |
| Artisan | 1 Emberbound Weave | 4 Source Gem | 1 Ember Lattice | 4 |
| Artisan | 1 Emberbound Weave | 4 Source Gem | 1 Bound Weave | 4 |
| Artisan | 1 Emberbound Weave | 4 Source Gem | 1 Tempered Weave | 4 |
| Artisan | 1 Emberbound Weave | 4 Source Gem | 1 Emberbound Quenched | 4 |
| Nobleman | 1 Rimebound Lattice | 4 Source Gem | 1 Frost Shard | 4 |
| Nobleman | 1 Rimebound Lattice | 4 Source Gem | 1 Silvered Flake | 4 |
| Nobleman | 1 Rimebound Lattice | 4 Source Gem | 1 Archive Leaf | 4 |
| Nobleman | 1 Rimebound Lattice | 4 Source Gem | 1 Rime Cord | 4 |
| Nobleman | 1 Rimebound Lattice | 4 Source Gem | 1 Lattice Blank | 4 |
| Nobleman | 1 Rimebound Lattice | 4 Source Gem | 1 Sealed Lattice | 4 |
| Noblewoman | 1 Rimebound Lattice | 4 Source Gem | 1 Rimebound Drawn | 4 |
| Noblewoman | 1 Rimebound Lattice | 4 Source Gem | 1 Rimebound Folded | 4 |
| Noblewoman | 1 Rimebound Lattice | 4 Source Gem | 1 Rimebound Stilled | 4 |
| Noblewoman | 1 Rimebound Lattice | 4 Source Gem | 1 Rimebound Rebound | 4 |
| Noblewoman | 1 Rimebound Lattice | 4 Source Gem | 1 Rimebound Quenched | 4 |
| Noblewoman | 1 Rimebound Lattice | 4 Source Gem | 1 Rimebound Layered | 4 |
| Lord | 1 Grave-Gilt Thread | 4 Source Gem | 1 Ash Of Names | 4 |
| Lord | 1 Grave-Gilt Thread | 4 Source Gem | 1 Mourning Dust | 4 |
| Lord | 1 Grave-Gilt Thread | 4 Source Gem | 1 Gilded Ash | 4 |
| Lord | 1 Grave-Gilt Thread | 4 Source Gem | 1 Debt Cord | 4 |
| Lord | 1 Grave-Gilt Thread | 4 Source Gem | 1 Reckoned Thread | 4 |
| Lord | 1 Grave-Gilt Thread | 4 Source Gem | 1 Grave Braid | 4 |
| Lady | 1 Grave-Gilt Thread | 4 Source Gem | 1 Settled Thread | 4 |
| Lady | 1 Grave-Gilt Thread | 4 Source Gem | 1 Gravegilt Drawn | 4 |
| Lady | 1 Grave-Gilt Thread | 4 Source Gem | 1 Gravegilt Stilled | 4 |
| Lady | 1 Grave-Gilt Thread | 4 Source Gem | 1 Gravegilt Rebound | 4 |
| Lady | 1 Grave-Gilt Thread | 4 Source Gem | 1 Gravegilt Layered | 4 |
| Lady | 1 Grave-Gilt Thread | 4 Source Gem | 1 Gravegilt Proofed | 4 |
| Prince | 1 Crown Filament | 4 Source Gem | 1 Heartwood Strand | 4 |
| Prince | 1 Crown Filament | 4 Source Gem | 1 Crowned Fibre | 4 |
| Prince | 1 Crown Filament | 4 Source Gem | 1 Yggdrasil Floss | 4 |
| Prince | 1 Crown Filament | 4 Source Gem | 1 Branch Cord | 4 |
| Prince | 1 Crown Filament | 4 Source Gem | 1 Living Crown | 4 |
| Prince | 1 Crown Filament | 4 Source Gem | 1 Woven Crown | 4 |
| Princess | 1 Crown Filament | 4 Source Gem | 1 Ninefold Thread | 4 |
| Princess | 1 Crown Filament | 4 Source Gem | 1 Crown Blank | 4 |
| Princess | 1 Crown Filament | 4 Source Gem | 1 Crown Drawn | 4 |
| Princess | 1 Crown Filament | 4 Source Gem | 1 Crown Folded | 4 |
| Princess | 1 Crown Filament | 4 Source Gem | 1 Crown Stilled | 4 |
| Princess | 1 Crown Filament | 4 Source Gem | 1 Crown Rebound | 4 |
| King | 1 Crown Filament | 2 Manipulation Essence | 1 Alfsteel Ingot | 2 |
| King | 1 Crown Filament | 2 Manipulation Essence | 1 Gaia Spirit | 2 |
| King | 1 Crown Filament | 2 Manipulation Essence | 1 Rune Pride | 2 |
| King | 1 Crown Filament | 2 Manipulation Essence | 1 Rune Wrath | 2 |
| King | 1 Crown Filament | 2 Manipulation Essence | 1 Rune Envy | 2 |
| King | 1 Crown Filament | 2 Manipulation Essence | 1 Rune Greed | 2 |
| Queen | 1 Crown Filament | 2 Abjuration Essence | 1 Crown Quenched | 4 |
| Queen | 1 Crown Filament | 2 Abjuration Essence | 1 Crown Layered | 4 |
| Queen | 1 Crown Filament | 2 Abjuration Essence | 1 Crown Proofed | 4 |
| Queen | 1 Crown Filament | 2 Abjuration Essence | 1 Crown Settled | 4 |
| Queen | 1 Crown Filament | 2 Abjuration Essence | 4 Manipulation Essence | 4 |
| Queen | 1 Crown Filament | 2 Abjuration Essence | 4 Conjuration Essence | 4 |

## Verification

Java 17 build and the existing 71 tests pass. The catalogue checker verifies
all item references against installed resources and the authored ladder, all
12 roles, bounded stock, Source payments and same-chain intermediate costs.
Feature-order validation reports no cycles.

`tools/run_elven_trade_validation.py` exercises the actual native MerchantMenu
payment/output slots and exact role catalogues for all 48 citizens (288 transactions), missing or short
payments, exhausted stock, saved offer/usage round trips and timed restocking.
The success report is `tools/elven_trades_build.json`. This is server gameplay
validation; client screen interaction remains pending. Restart Minecraft to
load the installed companion build.
