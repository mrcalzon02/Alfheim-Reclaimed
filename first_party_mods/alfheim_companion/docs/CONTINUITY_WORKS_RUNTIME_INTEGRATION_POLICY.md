# Continuity Works Runtime Integration Policy

Status: production integration and release-admission requirement for Alfheim Companion.

## Decision

Alfheim Companion and Continuity Works remain separate software components:

- separate repositories;
- separate source trees;
- separate JARs;
- separately versioned APIs and releases;
- no copied or forked Continuity Works generator implementation inside Alfheim Companion.

For the Alfheim Reclaimed distribution, Continuity Works is a first-class supported runtime component for advanced generated construction. The pack should ship a compatible Continuity Works JAR alongside Alfheim Companion.

The Companion's Forge dependency remains optional at loader level. This is deliberate: absence or failure of Continuity Works must degrade generated-construction capability rather than prevent the Companion from loading or corrupting existing Companion state.

## Responsibility boundary

### Alfheim Companion owns

- player intent capture;
- Companion identity, personality and dialogue;
- local inference orchestration;
- autonomous decision orchestration;
- authoritative player/Companion context capture;
- request/job persistence;
- owner preview and approval UX;
- inventory and material availability reporting;
- claim/ownership checks required by Companion behavior;
- deterministic task execution;
- FakePlayer-backed physical interaction with the world;
- construction progress, interruption and completion reporting.

### Continuity Works owns

- structure catalog and generator-provider authority;
- semantic construction vocabulary and legal candidate sets;
- structure interpretation and deterministic planning;
- geometry and compact blueprint production;
- palette/material planning;
- structural bounds and exclusion legality;
- blueprint validation;
- compact plan identity/integrity;
- placement stream production from an accepted compact plan.

### Inference owns only bounded semantic selection

The inference worker may help choose among capabilities and legal semantic alternatives exposed by the two deterministic systems. It must not author raw block lists, direct placements, commands, NBT/SNBT, or bypass validation.

The stable responsibility line is:

> Companion decides what needs building. Continuity Works decides how to design it. Deterministic Companion/FakePlayer systems physically build the accepted plan.

## Authoritative API boundary

The current in-process integration authority is the Continuity Works Compact Blueprint API and its decision-chain surface. At the time this policy was adopted:

- Compact Blueprint API: `1.8.0`;
- decision protocol: `cw-decision-1`;
- current Java authority: `io.continuityworks.api.blueprint.ContinuityWorksCompactBlueprintApi`.

The existing `CONTINUITY_WORKS_INFERENCE_COMPANION_API_HANDOFF.md` remains the detailed protocol contract. Continuity Works source remains authoritative when documentation and implementation disagree.

The Companion must feature-discover optional capabilities and fail closed on incompatible major versions or unknown required semantics. It must not duplicate the Continuity Works mutator dependency graph, generator legality rules, or geometry implementation.

## Runtime degradation contract

When Continuity Works is absent, incompatible, unavailable, or fails during a request, Alfheim Companion must remain usable.

The following Companion capabilities remain available when they do not independently require Continuity Works:

- summon, recall and dismiss;
- follow, wait, guard and defend;
- inventory and equipment;
- survival state;
- combat;
- ownership/lease behavior;
- deterministic dialogue;
- ordinary deterministic world interaction and tasks;
- quest/claim integrations;
- autonomous activities that do not require generated construction.

Generated structure design becomes unavailable. The Companion must report that state explicitly through deterministic dialogue/UI rather than pretending to have generated a plan.

Existing accepted construction jobs must enter a safe paused/stale/blocked state if their required Continuity Works authority is unavailable. They must never silently substitute a different generator or fabricate a plan.

## Distribution rule

Alfheim Reclaimed release packaging should include compatible JARs for both Alfheim Companion and Continuity Works. Their separation is an architectural boundary, not an instruction to make the player assemble the supported integration manually.

A standalone Alfheim Companion JAR may still load without Continuity Works because the Forge dependency is intentionally optional. Such an installation is a degraded-capability configuration, not the complete Alfheim Reclaimed construction stack.

## End-to-end construction admission gate

Advanced generated construction is not production-ready until the following round trip is demonstrated against the actual packaged versions:

1. Player issues an addressed construction request.
2. Companion captures authoritative owner, world, site, inventory and task context.
3. Companion creates a bounded Continuity Works `BlueprintRequest`.
4. Deterministic prefiltering resolves choices that do not require inference.
5. Optional inference selects only among legal semantic choices when needed.
6. Continuity Works validates/finalizes semantic decisions.
7. Continuity Works generates a compact blueprint plan.
8. Companion validates the returned plan through Continuity Works against current context.
9. Companion presents the owner preview/approval boundary.
10. Approval creates a deterministic construction task; rejection performs no world mutation.
11. Companion streams placements only as needed for execution rather than treating model text as geometry.
12. Every physical placement is executed through the approved deterministic world-interaction/FakePlayer path with current reach, inventory, claim and world checks.
13. Real materials are consumed/accounted for.
14. Interruption and restart preserve or safely invalidate the job according to persisted identity/version/context state.
15. Completion is reported only after the deterministic executor confirms completion.

## Required negative admission cases

The admission suite must also prove safe behavior for:

- Continuity Works JAR absent;
- incompatible API major;
- capability unavailable;
- timeout/cancellation;
- malformed or stale decision output;
- stale candidate dictionary/revision;
- plan validation rejection;
- insufficient materials;
- claim denial;
- unreachable/obstructed placement;
- world change after plan generation;
- owner rejects preview;
- server restart during decision/planning;
- server restart during construction;
- inference worker absent;
- inference worker failure during planning;
- Continuity Works becoming unavailable during an active job.

In every failure case, model text must remain non-authoritative and world mutation must fail closed.

## Release significance

This policy prevents two failure modes:

1. merging or copying Continuity Works generation logic into Alfheim Companion and creating divergent implementations;
2. making Continuity Works a hard Companion boot dependency and thereby breaking unrelated Companion functionality when advanced construction is unavailable.

The supported Alfheim Reclaimed product ships the two JARs together, pins compatible versions, tests their real integration, and preserves graceful degradation at the Companion boundary.