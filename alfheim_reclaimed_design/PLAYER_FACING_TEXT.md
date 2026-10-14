# Crafting and material descriptions

User instruction, 2026-10-13: player text must describe crafting and magical processes rather
than numbered eras. An intermediate must explain its identity, origin and next use.

The displayed workings are Grovecraft, Mana Quickening, Verdant Grafting, Gateweaving,
Elementium Alloy Binding, Fey Sinew Binding, Ember Tempering, Frost-Memory Inscription,
Ancestral Threadbinding and World-Tree Crownweaving. These names describe the work; the
individual instructions name the actual station or method.

`tools/player_text.py` supplies shared display vocabulary. Quest generators apply it only to
displayed prose, leaving keys and IDs alone. `gen_ladder.chain_description` derives each stage's
origin, current method, next material and next method from the same chain and station rotation
that emits its recipes. The `brew` station key currently emits shapeless crafting, so displayed
instructions correctly say shapeless crafting. Names do not imply unimplemented effects.

`tools/refresh_player_text.py` refreshes the 83 stage items and regalia descriptions, edits quest
prose in the game's existing SNBT layout, and generates crafting-route tooltips for 427 custom
objects. It changes no quest IDs, rewards, dependencies, positions, recipe inputs or outputs.
`tools/gen_items.py --text-only` refreshes registrations without redrawing assets.

`tools/gen_process_tooltips.py` derives routes from authored KubeJS recipes and data recipes.
Shift shows where an object is made and what it produces; ingredient groups are labelled, and
available mana, Source and aura costs are included. Long lines wrap; at most six origins and six
uses appear, with a JEI pointer for further routes. These are descriptions of authored routes,
not a runtime recipe registry or a replacement for JEI's quantities, layouts and alternatives.
Regenerate after recipe changes. World acquisition lore remains in existing descriptions and
the Compendium. Internal numbering remains developer metadata for compatibility.

Validation: static validated. The full existing progression/recipe-schema check reports zero
problems. Quest IDs, task types, rewards, dependencies and positions match their prior values.
All 83 stage descriptions contain meaningful prose; all finished and intermediate materials
have source and use routes. All 427 tooltip handlers execute under a simulated client event
with and without Shift, and generated output reproduces exactly. The installed KubeJS jar
confirms the tooltip callback signature, modifier API and additive registration tooltips.
An in-game restart and visual verification of the resulting tooltip layout remain outstanding.
