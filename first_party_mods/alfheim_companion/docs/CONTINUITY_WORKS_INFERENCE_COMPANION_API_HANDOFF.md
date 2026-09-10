# Continuity Works — Inference Engine & Alfheim Companion API Handoff

**Companion repository:** `mrcalzon02/Alfheim-Reclaimed`  
**Companion location:** `first_party_mods/alfheim_companion/`  
**Continuity Works authority:** `mrcalzon02/Continuity-Works`, `main`  
**Continuity Works baseline used for this handoff:** `52093275a6d43510c1c1bf5cc5d81545266f26b2`  
**Compact Blueprint API:** `1.8.0`  
**Decision protocol:** `cw-decision-1`  
**Reference inference workload:** Qwen 2.5 Instruct Q4-class or another comparably small real-time local controller  
**Maximum inference output:** 64 tokens per decision call; 32 or fewer preferred

## 1. Authority and integration objective

This document is the direct implementation contract for the AI/developer preparing the Alfheim Companion inference engine integration. It is intentionally designed for expansion. The companion must not hard-code the present decision vocabulary, transport, inference backend, prompt format, candidate ranking method, cache, or persistence implementation as permanent architecture.

Current Continuity Works source remains authoritative if this handoff and implementation disagree. Feature discovery must therefore happen at runtime.

The stable architectural invariant is:

> **Inference selects. State accumulates. Catalog defines. Generator builds. Validator decides legality.**

The local model is a semantic controller, not a structure generator. It must never be asked to author raw block lists, NBT/SNBT, commands, jigsaw geometry, collision volumes, structure exclusion logic, loot-table bodies, primitive placement operations, or direct world mutations.

The companion owns orchestration. Continuity Works owns semantic legality, catalog authority, deterministic planning, primitive geometry, materials, validation, exclusion rules, and materialization.

## 2. Forward-compatible design rules

The integration must preserve these rules even as the systems evolve:

1. **Discover capabilities rather than hard-code them.** The current mutator set is not guaranteed to remain exhaustive.
2. **Keep rich state outside the model.** Model output is ephemeral; request state, decision revision, candidate dictionaries, fingerprints, and blueprint identity are durable machine state.
3. **Use many tiny decisions instead of one large generation response.** A typical answer should be 2–20 tokens and often only one mutation.
4. **Prefer deterministic resolution before inference.** User choices, hard constraints, inheritance, context rules, caches, and ranked prefilters should eliminate model calls whenever possible.
5. **Repair only invalidated branches.** Changing an upstream decision should invalidate dependent decisions, not force the entire structure request to restart.
6. **Allow redundancy at validation boundaries, not in implementations.** The companion may verify dictionary/revision integrity and Continuity Works should validate again, but the companion must not duplicate Continuity Works geometry or legality logic.
7. **Fail closed on unknown required behavior.** Never guess an unsupported required capability, unresolved ID, stale dictionary, failed placement, or incompatible API major.
8. **Keep transports replaceable.** In-process Java is authoritative now; a future HTTP, IPC, socket, JNI, sidecar, or other bridge must map to the same semantics.
9. **Version meaningful boundaries independently.** API, decision protocol, model configuration, companion integration, candidate dictionaries, prompts, compact plan format, and later edit protocols should be separately identifiable.
10. **Preserve extension space.** Unknown optional metadata should be tolerated where the negotiated protocol allows it. Unknown required semantics must be surfaced as a structured failure.

## 3. Trust boundaries

| Component | Owns | Must not own |
|---|---|---|
| Inference engine | selection/ranking among legal semantic choices | blocks, NBT, world mutation, placement legality, exclusion policy |
| Alfheim Companion | context capture, orchestration, model calls, persistence, retries, UI/telemetry | parallel Continuity Works generator/validator |
| Continuity Works decision chain | mutators, dependencies, revision, parsing, semantic validation/finalization | model runtime/weights |
| Continuity Works generator | catalog resolution, deterministic planning, primitives, palettes/materials | model reasoning |
| Continuity Works validator | bounds, semantic resolution, material/site/world legality | guessing unavailable context |
| Minecraft runtime | authoritative live world and server-thread mutation | long-running model inference |

Model output is always untrusted input. Validation success cannot be fabricated by the companion or inferred from model confidence.

## 4. Current Java API surface

The current authority is:

`io.continuityworks.api.blueprint.ContinuityWorksCompactBlueprintApi`

Implemented methods include:

```java
BlueprintApiVersion apiVersion();
BlueprintVocabulary vocabulary();
CompletableFuture<CompactBlueprintPlan> generateCompact(BlueprintRequest request);
ValidationResult validateCompact(CompactBlueprintPlan plan, BlueprintContext context);
MaterialManifest getCompactMaterials(UUID blueprintId);
void cancelCompact(UUID requestId);

BlueprintDecisionChain.Profile decisionProfile();
BlueprintDecisionChain.State beginDecision(BlueprintRequest request);
BlueprintDecisionChain.Step nextDecision(BlueprintDecisionChain.State state);
BlueprintDecisionChain.State applyDecision(BlueprintDecisionChain.State state, String encodedMutations);
BlueprintDecisionChain.Validation validateDecision(BlueprintDecisionChain.State state);
BlueprintDecisionChain.FinalizedDecision finalizeDecision(BlueprintDecisionChain.State state);

long streamPlacements(CompactBlueprintPlan plan, CompactPlacementSink sink);
CompactBlueprintPlan applyEdit(CompactBlueprintPlan plan, String encodedIntent);
CompactBlueprintPlan applyEdit(
    CompactBlueprintPlan plan,
    String encodedIntent,
    CompactBlueprintModuleResolver modules
);
```

The decision-chain methods are default methods on the compact API so providers do not need a second decision engine.

`BlueprintApiVersion.CURRENT` is `1.8.0`. Current compatibility is major-version compatibility. The companion must still feature-detect optional capabilities instead of using minor versions as behavior switches.

## 5. BlueprintRequest and semantic specifications

`BlueprintRequest` carries context that should not be repeatedly serialized through inference:

```text
requestId
companionUuid
ownerUuid
dimensionId
buildPurpose
constructionVolume
preferredOrigin
preferredFacing
specifications
availableMaterials
candidateSites
permittedStyles
```

Required values are non-null, `dimensionId` and `buildPurpose` are non-blank, and `preferredOrigin` must be inside the construction volume.

`BlueprintSpecification` intentionally uses open string keys/values rather than a closed Java enum:

```text
key
value
requirement = REQUIRED | PREFERRED | AVOID
```

This is a deliberate ABI extension seam. Do not create a giant companion-side switch that assumes current semantic keys are exhaustive. Unsupported **required** specifications must fail visibly rather than disappear silently.

## 6. Tiny-inference decision protocol

Protocol: `cw-decision-1`.

Decision state is carried outside inference:

```text
requestId   UUID
revision    non-negative long
selections  Map<mutatorCode, semanticValue>
finalized   boolean
```

Every accepted mutation increments the revision. Finalization increments it again and freezes the state. Late inference results whose revision no longer matches current state must be discarded.

The current mutators are:

| Code | Meaning | Source | Depends on | Required | Current fixed values |
|---|---|---|---|---|---|
| `A` | archetype/catalog ID | structure catalog | none | yes | dynamic |
| `Z` | scale | fixed | `A` | yes | `S/M/L` |
| `B` | biome/environment adaptation | archetype profile | `A` | yes | dynamic |
| `C` | culture variant | archetype profile | `A` | no | dynamic |
| `F` | family mode | fixed | `A` | yes | `I/P` |
| `O` | orientation, capital letter O | fixed | `B` | no | `AUTO/N/E/S/W` |
| `Q` | condition/state | archetype profile | `A` | no | dynamic |
| `K` | palette profile | archetype + biome | `A,B` | no | dynamic |
| `D` | detail density | fixed | `A,Z` | no | `L/N/H` |

`I` means independent placement. `P` means explicit same-parent compatible-family composition.

**Do not hard-code this list as permanent.** Enumerate mutators from `decisionProfile().mutators()` and `nextDecision().nextMutators()`.

### Dependency invalidation

When a selection changes, Continuity Works recursively removes dependent downstream choices and preserves unrelated state. Example: changing `B` invalidates `O` and `K`; changing `A` invalidates every archetype-dependent branch.

The companion must accept returned state as authoritative rather than maintaining a parallel dependency graph.

## 7. Mutation wire grammar and inference budget

Accepted form:

```text
CODE=VALUE
```

Multiple mutations may be separated by semicolons/newlines, although one mutation is preferred when decisions are dependent:

```text
Z=M;F=I
```

Current limits:

```text
model output ceiling:       64 tokens
preferred output:           <=32 tokens
mutations per response:     <=4
wire characters:            <=256
value characters:           <=64
```

Fixed values normalize to uppercase. Dynamic catalog/resource values preserve semantic identity after trimming. Allowed value characters are letters, digits, `_`, `-`, `.`, `:`, `/`.

The parser rejects malformed fields, duplicate fields, invalid fixed values, illegal characters, control characters, unmet dependencies, empty output, mutations after finalization, and raw-world keys such as BLOCK/NBT/SNBT/COMMAND/PLACEMENT/OPERATION/PRIMITIVE families.

Inference output should contain only requested mutation syntax. No Markdown, prose, JSON wrapper, explanation, or chain-of-thought is required.

## 8. Dynamic candidate dictionaries — required next optimization layer

Fixed mutators already expose exact legal values. Dynamic mutators currently declare their authoritative source but still need complete API-bound candidate sets.

The companion must be designed for request/state-specific dictionaries:

```text
DecisionChoiceSet
  mutatorCode
  dictionaryId
  dictionaryVersion
  choices[]
    localCode
    semanticValue
    label?
    scoreHints?
    metadata?
```

Example brief:

```text
CW1 R=4 NEXT=B
CTX river temperate low_slope
0=riverbank 1=gravel_bar 2=wooded_bank 3=floodplain
OUT B=<0-3> ONLY
```

Expected model output:

```text
B=2
```

The local code is **ephemeral**. Before authoritative mutation, it resolves to `B=wooded_bank`. A local numeric index must never become the final semantic ID.

Dictionary rules:

- dictionaries are state/request specific and bounded;
- persist dictionary ID/version when a job can resume;
- reject choices from a stale dictionary;
- preserve catalog/resource semantic IDs exactly;
- progressively narrow large catalogs instead of dumping them into context;
- allow ranking metadata without making rank itself authoritative;
- if only one legal candidate remains, select it deterministically and skip inference.

This layer is the primary route to routine 2–10 token inference calls.

## 9. Consecutive inference strategy

The companion should not force every structure through every step. The baseline decision chain is:

```text
0 deterministic prefilter from request/world context
1 archetype selection A
2 scale/family Z,F when not already implied
3 environment B
4 culture/condition C,Q only when meaningful
5 orientation/palette/detail O,K,D only when unresolved
6 validate
7 repair only failed/invalidated branch
8 finalize
```

Prefer decisions in this order:

```text
explicit user choice
hard legality constraint
deterministic inheritance
deterministic context mapping
valid cached decision
ranked deterministic prefilter
tiny inference
larger/secondary inference only as exceptional escalation
```

Examples: a forced shoreline orientation needs no `O` inference; a same-parent jigsaw child may inherit `F=P`; a construction volume allowing only one scale needs no `Z` inference; a uniquely viable palette needs no `K` inference.

## 10. InferenceAdapter contract

Continuity Works remains model-agnostic. The companion should isolate the local model behind an adapter:

```text
InferenceRequest
  requestId
  decisionRevision
  protocolVersion
  modelProfile
  maxOutputTokens
  prompt
  stopSequences
  timeoutPolicy
  metadata

InferenceResult
  requestId
  decisionRevision
  rawOutput
  tokenCount
  finishReason
  elapsedNanos
  modelInstanceId
  configFingerprint
```

Recommended behavior:

- hard-enforce 64 output tokens;
- normally request far less;
- use deterministic/low-temperature decoding where supported;
- use a stop condition appropriate to one-line mutation output;
- never report success after timeout/parse/backend failure;
- cap retries and queued jobs;
- never run inference on the Minecraft server thread.

Keep prompt templates separately versioned so prompt compression/tuning can change without changing API semantics. Keep model routing replaceable so later decisions may use rules, classifier heads, another tiny model, or selective larger-model escalation.

## 11. Companion job lifecycle and persistence

Structure generation should be a resumable job:

```text
REQUEST_CAPTURED
CONTEXT_SNAPSHOTTED
DECISION_STARTED
DECISION_IN_PROGRESS
DECISION_VALID
DECISION_FINALIZED
PLAN_GENERATING
PLAN_GENERATED
PLAN_VALIDATING
PLAN_ACCEPTED
CONSTRUCTION_READY
CONSTRUCTION_RUNNING
CONSTRUCTION_COMPLETE
```

Failure/repair states should include:

```text
WAITING_FOR_CONTEXT
WAITING_FOR_INFERENCE
INFERENCE_RETRYABLE_FAILURE
INFERENCE_PARSE_FAILURE
DECISION_BLOCKED
PLAN_REJECTED
MATERIAL_SHORTAGE
WORLD_CHANGED
STALE
CANCELLED
```

Persist semantic boundaries, not every block placement. At minimum retain:

```text
request UUID
owner/companion UUID
API + protocol version
decision revision + selections
candidate dictionary IDs/versions
model profile/config fingerprint
raw compact model output
final specifications
world/context fingerprints
blueprint UUID/version/integrity hash
validation findings
timings
```

Do not persist hidden model reasoning.

On restart, resume only if protocol/API compatibility, context fingerprints, dictionary validity, and blueprint/world assumptions still hold. Otherwise mark the affected layer stale and recompute only that layer.

## 12. Compact generation, validation, edits, and execution

After finalization, generate through `generateCompact(BlueprintRequest)`. The immutable `CompactBlueprintPlan` includes blueprint identity/version/integrity, dimension and construction volume, dimensions/anchor/facing, specification resolutions, palette/material manifest, compact primitives, material issues, workload estimate, preview metadata, confidence, and warnings.

Keep the compact plan/UUID rather than duplicating a full block list. Stream placements only when construction execution needs them.

Always call `validateCompact(plan, context)` before treating a plan as buildable. Revalidate after relevant world/context changes and semantic plan edits.

Post-plan edit semantics are separate from decision-chain semantics:

```text
TRANSLATE
ROTATE
MIRROR
PALETTE_REMAP
COMPOSE
REPEAT
```

These remain bounded and validated. If this surface grows, it should become its own independently versioned inference protocol instead of bloating `cw-decision-1`.

## 13. World safety, materials, threading, and cancellation

Continuity Works remains authoritative for collision/exclusion legality. The companion/inference layer must never waive structure exclusion, infer family overlap merely from similar IDs, force a failed placement, reinterpret an exclusion radius, or place a jigsaw child outside its explicit same-parent contract.

Current Continuity Works policy requires at least **500 blocks** between unrelated structures, including per-jigsaw-piece protection. Same-parent compatible composition is a narrow exception and never permits illegal physical overlap.

Materials are context, not free-form AI output. Continuity Works should resolve/rank viable material or palette profiles before inference. The model chooses only among legal alternatives when a real semantic choice remains.

World/site reads are captured on the authoritative game thread, converted to immutable context, and then handed to planner/inference workers. Before actual construction, validate again against current world state.

Honor `cancelCompact(requestId)` and cancel corresponding inference work. Reject late results by request/revision identity.

## 14. Caching, integrity, retries, and security

Recommended caches include API/decision profile, catalog index by fingerprint, candidate dictionaries by revision/source fingerprint, deterministic context classification, normalized biome/site profiles, palette viability, and safe compact-plan results keyed by request/spec/context fingerprint.

Do not indefinitely cache mutable world-placement legality, inference without revision/model fingerprints, or numeric candidate indices without dictionary identity.

Failure classes must be explicit:

- **parse/protocol:** one constrained retry, then visible failure;
- **stale state/dictionary:** discard and fetch current state;
- **missing context:** acquire context, do not guess;
- **semantic validation:** repair affected branch only;
- **plan validation:** deterministic alternatives first, inference only if needed;
- **world changed:** revalidate and preserve still-valid semantic state;
- **model backend:** deterministic fallback only when a legal deterministic policy exists.

Never execute model text as commands, arbitrary NBT/SNBT, file paths, or module IDs not present in an authoritative legal set. Bound payload sizes, retries, queue depth, and inference time.

The compact plan’s integrity hash is authoritative for plan identity; model output is not.

## 15. Extensibility and transport-neutral integration

Recommended companion abstractions:

```text
ContinuityWorksAdapter
  discover
  beginDecision
  getNextDecision
  applyDecision
  validateDecision
  finalizeDecision
  generateCompact
  validateCompact
  applyEdit
  streamPlacements
  cancel

InferenceAdapter
  infer

DecisionPolicy
  chooseNextMutator
  buildBrief
  shouldInfer
  deterministicFallback

StateStore
  save
  load
  invalidate

ContextProvider
  snapshotWorldContext
  fingerprint
```

Future mutators should be data-described with fields such as:

```text
wireCode
semanticKey
protocolNamespace
valueSource
required
dependencies
choiceMode
maxChoices
invalidationGroup
validationClass
promptHint
uiHint
deprecation
replacementCode
extensions
```

Future choice modes may include `FIXED`, `CATALOG`, `ARCHETYPE_PROFILE`, `CONTEXT_DERIVED`, `RANKED_DYNAMIC`, `INHERITED`, and `DETERMINISTIC_ONLY`.

Potential later semantic layers include settlement role, infrastructure relationship, ruin chronology, room/program emphasis, terrain fitting, entrance/accessibility strategy, loot/occupancy profile, structural density, and performance/detail budgets. The companion should route unknown discovered mutators generically where possible.

### Future HTTP/IPC bridge

The current authoritative implementation is in-process Java. Do **not** assume these routes exist yet, but a future thin bridge may expose:

```text
GET  /v1/blueprints/decision/profile
POST /v1/blueprints/decision/begin
POST /v1/blueprints/decision/next
POST /v1/blueprints/decision/apply
POST /v1/blueprints/decision/validate
POST /v1/blueprints/decision/finalize

POST /v1/blueprints/compact/generate
POST /v1/blueprints/compact/validate
POST /v1/blueprints/compact/edit
POST /v1/blueprints/compact/cancel
```

Any bridge must call the same Continuity Works authority and use its existing publication/OpenAPI/serviceability model. It must not become a shadow decision implementation.

A transport-neutral envelope should carry API/protocol version, request ID, revision, operation, required capabilities, payload, findings, and an open `extensions` object. Unknown optional extensions may be ignored; unknown required capabilities must fail.

## 16. Integration acceptance tests

Before construction execution is considered integrated, automated tests should cover:

- API/protocol negotiation and major mismatch;
- unknown optional versus required capability behavior;
- all mutation parser limits and forbidden raw-world keys;
- dependency exposure and recursive invalidation;
- stale revision rejection;
- dynamic candidate dictionary binding and stale dictionary rejection;
- preservation of semantic IDs;
- timeout, malformed output, prose output, empty output, backend crash, retry cap;
- deterministic fallback behavior;
- final specifications reaching compact generation;
- compact integrity and bounds validation;
- required revalidation after edits/world changes;
- restart/resume and fingerprint changes;
- no inference on server thread;
- bounded queue/retry/catalog narrowing;
- no full block list entering inference context;
- 500-block unrelated-structure exclusion remaining non-bypassable;
- same-parent mode never authorizing illegal physical overlap.

## 17. Recommended implementation milestones

1. **API discovery:** load compact API, verify version/profile, no generation.
2. **Scripted decision harness:** begin/next/apply/validate/finalize without a model.
3. **Tiny inference adapter:** prove exact compact responses below 64 tokens.
4. **Candidate dictionaries:** bind dynamic choices and ephemeral numeric/short codes.
5. **End-to-end generation:** finalized decisions drive `generateCompact` and `validateCompact`.
6. **Persistence/resume:** survive game restart with revision/fingerprint integrity.
7. **Semantic plan edits:** bounded translate/rotate/mirror/palette/compose/repeat.
8. **Construction execution:** streamed placements, server authority, cancellation.
9. **Optimization:** deterministic shortcuts, caching, ranked prefilters, model routing, prompt compression, hardware tuning.
10. **Optional bridge:** HTTP/IPC only if needed, mapping to the same semantics.

## 18. Current known boundary and source map

As of the Continuity Works baseline used here:

- compact Java decision chain is implemented;
- API version is `1.8.0`;
- decision protocol is `cw-decision-1`;
- the Java inference-facing decision harness has been validated in Continuity Works;
- dynamic candidate binding is the next required inference-facing layer;
- the decision-chain HTTP bridge is not yet a published/executable API;
- Continuity Works remains model-agnostic.

Primary Continuity Works source files:

```text
modules/continuityworks-api/src/main/java/io/continuityworks/api/blueprint/
  BlueprintApiVersion.java
  ContinuityWorksCompactBlueprintApi.java
  BlueprintDecisionChain.java
  BlueprintRequest.java
  BlueprintSpecification.java
  CompactBlueprintPlan.java
  CompactEditIntent.java
  CompactBlueprintEditExecutor.java
  CompactBlueprintModifier.java
  CompactBlueprintMaterializer.java
  CompactPlacementSink.java

docs/
  API.md
  BLUEPRINT_RUNTIME_BUDGET.md
```

## 19. Final architecture position

The Alfheim Companion should not become an AI structure generator with Continuity Works attached to it. It should remain a **stateful orchestration layer** that asks a replaceable tiny inference engine a sequence of narrow semantic questions and hands those bounded choices to Continuity Works.

The stable center is:

```text
DISCOVER
-> SNAPSHOT CONTEXT
-> RESOLVE DETERMINISTIC FACTS
-> ASK ONE LEGAL QUESTION
-> APPLY ONE BOUNDED MUTATION
-> VALIDATE
-> REPEAT ONLY WHEN NECESSARY
-> FINALIZE SEMANTICS
-> GENERATE COMPACT PLAN
-> VALIDATE PLAN
-> APPLY BOUNDED EDITS IF NEEDED
-> REVALIDATE
-> STREAM/MATERIALIZE ONLY FOR EXECUTION
```

Inference backend, transport, ranking, caching, prompt formatting, persistence, and optimization layers must remain replaceable. Continuity Works remains the deterministic kernel and single structure-authority implementation.
