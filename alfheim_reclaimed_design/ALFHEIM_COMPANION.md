# Alfheim Companion — Design and Implementation Plan

Status: **prototype / static validation**  
Mod ID: `alfheim_companion`  
Target: Minecraft 1.20.1, Forge 47.4.10, Java 17  
Continuity Works blueprint API: version 1

## Purpose

Alfheim Companion adds one persistent, summonable elven companion to a server. The companion is a
local Minecraft entity with its own identity, memory, inventory and state. Normal movement, combat,
defence, retreat, following and interaction mechanics are deterministic Minecraft/Forge routines.
A very small local language model is reserved for ambiguous construction planning and occasional
ambient dialogue; it never directly mutates the world.

## Non-negotiable rules

1. Exactly one companion may exist at a time across all dimensions on the server.
2. The companion is a real local mob, not a remote service, player subclass, or owner impersonation.
3. It is summoned or recalled with the craftable `companion_sigil`; crouch-use dismisses it.
4. Summoning and dismissal use Enderman teleport particles and sound.
5. Summoning chooses a safe location no farther than five blocks from the owner.
6. A name is selected from a bounded elven name list on first creation and persists with memory.
7. Rapid repeated summoning raises a persistent agitation counter. Agitation affects preset dialogue
   and decays by one point per five in-game minutes. It never weakens safety or obedience.
8. Commands are recognized only when prefaced with the companion's current name, for example
   `Aelara, follow`. Unaddressed chat is ignored.
9. Destructive actions obey FTB claims. When FTB Chunks is installed but no compatible claims adapter
   is registered, destructive actions fail closed.
10. The companion asks before accepting or equipping an offered item. A second matching offer within
    ten seconds confirms the transfer.
11. Items, ingredients and placed blocks must come from real inventories. Nothing may be created from
    nothing unless the requesting player is in creative mode.
12. The inference engine is inactive when the companion is dismissed. Routine commands and behaviors
    do not invoke inference.

## Runtime layers

### Native behavior layer

Minecraft goals and later SmartBrainLib behaviors own navigation, following, guarding, defending,
retreating, pickup, delivery, interaction cooldowns and animation. Combat does not wait for inference.

### Programmatic task layer

Typed Java tasks cover:

- `follow`;
- `guard` at the current or named position;
- locate an item and either **show its location**, **fetch it**, or **lead the owner to it**;
- fetch a requested quantity for a quest or direct request;
- explain and assist with crafting an item using actual known recipes and inventories;
- request, preview and execute a named construction blueprint;
- resume, suspend, cancel and report task progress.

Searches are bounded and claim-aware. Container extraction requires permission and a real matching
stack. Crafting consumes real ingredients and uses registered recipes. Building consumes real blocks
and validates each operation immediately before execution.

### Tiny reasoning layer

Target model: `Qwen2.5-0.5B-Instruct` in Jlama Q4 form (about 316 MB of model files), or another
drop-in engine satisfying the same `TinyBrainEngine` contract. The inference subsystem target is less
than 1 GB of disk and working memory, with a 512-token context, at most 64 output tokens and one active
request globally.

Because current Jlama requires Java 21 preview features while Forge 1.20.1 officially targets Java 17,
Jlama cannot simply be shaded into the Forge mod. The adapter must either be a separately bundled local
Java 21 worker or be replaced by a verified Java-17-compatible engine. Until then, a deterministic rule
engine implements the interface.

The model receives candidate choices, not raw chunks or unrestricted control. A compact result names a
known task, template, site and parameters. Java parses, validates and executes it. Invalid, late or stale
results are discarded.

## Passive context and dialogue

Routine conversation comes from bounded preset banks of adjectives, summon/dismiss lines, activity
comments and interaction responses. This avoids spending inference on predictable speech.

An ambient reflection request may occur only when all of these are true:

- the companion is summoned and the owner is nearby;
- the area is calm and no urgent behavior is active;
- no task or inference request is running;
- the cooldown has elapsed (initial target: ten minutes);
- the server is not under measured tick pressure.

The ambient model input is a compact, immutable snapshot: dimension, biome, weather/time category,
current activity, a few nearby semantic features, one active quest summary and up to three relevant
memories. Its output is dialogue only. It cannot select or execute an action.

## Persistent memory and state

Authoritative memory lives in overworld `SavedData`, not large entity NBT or client-synced tags.
Entity NBT contains only immediate identity, mode, equipment and inventory state needed to restore the
mob. Current memory bounds are 50 episodic entries and 64 semantic facts.

Memory domains:

- identity: persistent name, owner UUID and companion UUID;
- relationship: familiarity, preferences, promises and boundaries;
- state: following, waiting, guarding, defending, retreating, working or dismissed;
- task: objective, requested quantity, approach, progress, failure and blueprint reference;
- episodic: bounded important events with type, subject, detail, time and importance;
- semantic: landmarks, known resources, machines, work sites and player preferences;
- quest: selected quest IDs, status transitions and notable objective progress;
- personality: agitation and dialogue variation state.

The model may propose a memory, but Java decides whether it is supported, safe, useful and within
bounds before saving it.

## Quest awareness

An optional, versioned FTB Quests adapter normalizes quests into:

- stable quest ID and display name;
- goal/description;
- status: not available, available, active or completed;
- objective descriptions and current/required counts;
- ingredient or tag requirements and known availability;
- completion criteria.

The companion can reference quests by name, goal, ingredient or criterion in addressed chat. Full quest
graphs are not copied into memory or prompts. The adapter supplies current views, while memory retains
only selected objectives and significant changes.

## Continuity Works integration

Continuity Works implements the versioned `BlueprintProvider` Java endpoint. Alfheim Companion submits
immutable requests containing purpose, maximum bounds, styles, available materials, preferred origin,
orientation and pre-scored candidate sites. Continuity Works returns a proposal containing an ID,
format version, integrity hash, origin, bounds, placements, material manifest and warnings.

Required flow:

1. addressed build request becomes a typed task;
2. deterministic code gathers materials and candidate sites;
3. tiny reasoning selects or clarifies purpose/style when necessary;
4. Continuity Works generates a proposal from the immutable request;
5. the server creates a fresh world snapshot and Continuity Works validates the proposal;
6. the owner receives a preview and explicitly approves destructive work;
7. a deterministic executor revalidates claims, chunks, reach, inventory and block state per step;
8. memory records only blueprint identity, location, decisions and progress—not the entire block list.

Only one blueprint request can exist for the singleton companion. Continuity Works is optional: without
it, only bundled static templates are available.

## Player-like capabilities and permissions

The entity owns an 18-slot inventory plus normal equipment slots. Validated block actions run through a
dedicated Forge `FakePlayer` identity so Forge events and protection hooks observe them. The fake player
never uses the owner's UUID or privileges. Claim checks occur before the vanilla/Forge action path and
again where needed at execution.

Player-like capability means using legitimate player interaction paths—not bypassing claims, commands,
recipes, inventories, reach, cooldowns or game mode. Direct command execution and arbitrary reflection
into other mods are prohibited.

## Chunk loading

The companion will hold a small, moving, ticking Forge chunk ticket centered on its current chunk while
active. The initial cap is the current chunk plus the minimum neighboring radius required for safe
navigation. Old tickets are released before new tickets are acquired, and all tickets are released on
dismissal, death and server shutdown. It must not force-load arbitrary goals, entire paths or dimensions.

This controller remains pending until its exact Forge 47.4.10 behavior is verified in a controlled
server run.

## Implemented prototype

- official Forge 47.4.10 Gradle project and metadata;
- registered companion entity and temporary player-model renderer;
- craftable summoning sigil;
- server-wide singleton registration and recall service;
- persistent name, location, state, memory, task reference and agitation data;
- bounded episode/fact memory collections;
- owner following/waiting behavior;
- persistent 18-slot inventory and two-step item offer confirmation;
- Enderman-style teleport effect utility;
- deterministic tiny-brain interface and bounded single-request coordinator;
- fail-closed claims bridge;
- player-like break/place service and creative-only generation gate;
- versioned Continuity Works blueprint endpoint;
- versioned FTB Quests awareness endpoint;
- preset name and dialogue banks.
- name-prefixed chat parser for follow, guard, status, cancel, item, craft, build and quest requests;
- guard-anchor goal and bounded dropped-item show/fetch/lead routines;
- registered-recipe crafting advice with combined owner/companion material checks;
- bounded 3×3 moving ticking chunk ticket with dismissal, death and shutdown cleanup;
- low-frequency quest status memory refresh;
- ten-minute calm-state ambient reflection boundary with dialogue-only output.

## Next implementation order

1. Replace string task persistence with a versioned typed task codec and resume semantics.
2. Extend item search from visible drops to remembered, permission-approved container indexes.
3. Add inventory-backed recipe execution after an explicit craft confirmation.
4. Implement blueprint request lifecycle, preview, explicit approval and execution ledger.
5. Add the FTB Chunks and FTB Quests 1.20.1 version-specific adapters.
6. Measure and tune the 3×3 chunk-ticket radius under representative server load.
7. Implement a Java-17-compatible tiny-model adapter or isolated bundled Jlama worker.
8. Add GameTests, dedicated-server tests and tick/memory profiling.
9. Replace the temporary player renderer with approved Hollow Court assets.

## Acceptance gates

Compilation is only static validation. Production admission additionally requires a dedicated server
boot, singleton/dimension tests, claim tests, survival inventory accounting, quest compatibility,
Continuity Works contract tests, chunk-ticket cleanup tests, malformed/stale inference tests, and a
measured tick/RAM budget under representative modpack load.
