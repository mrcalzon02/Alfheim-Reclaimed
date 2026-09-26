# Deterministic Dialogue Jigsaw

Status: production requirement for Alfheim Companion.

## Purpose

Alfheim Companion must retain a coherent character voice and useful contextual speech without requiring the optional inference worker. Routine acknowledgements, task reporting, autonomous commentary, refusals, failures, and state descriptions should be produced locally by deterministic Java code. The inference worker remains an optional semantic/conversational reasoning layer rather than the baseline dialogue generator.

## Response hierarchy

1. Fixed safety/system response when exact wording or unambiguous reporting is required.
2. Deterministic Dialogue Jigsaw for routine and contextual speech.
3. Optional inference-enhanced dialogue when the request genuinely requires semantic composition or interpretation.
4. Immediate deterministic fallback if inference is disabled, unavailable, malformed, cancelled, or late.

Inference failure must never suppress ordinary Companion speech or ordinary deterministic behavior.

## Typed fragment model

The composer assembles grammar-compatible typed fragments rather than concatenating arbitrary strings. Initial semantic fragment classes should include:

- OPENING / GREETING
- ACK_POSITIVE / ACK_NEGATIVE / ACK_UNCERTAIN
- INTENT
- ACTIVITY / TASK
- TARGET
- QUANTITY
- LOCATION
- STATE
- OBSERVATION
- REASON
- PROGRESS
- RESULT
- REQUEST_ALTERNATIVE
- PERSONALITY_MODIFIER
- CLOSING

Components are optional. Missing components must disappear cleanly without broken punctuation or grammar. Values such as companion name, owner name, item, block, quantity, biome, location, task and objective are supplied as typed substitutions rather than model-authored facts.

## Authoritative-state rule

The dialogue system describes authoritative game state; it does not invent authoritative game state.

For example, Java may supply:

- TASK = GATHER
- TARGET = OAK_LOG
- COUNT = 16
- RESULT = CLAIM_DENIED

The composer may realize that as a personality-appropriate sentence such as, "I found the trees, but I cannot harvest there." It may not independently decide that a claim denied access, change the requested quantity, claim that items were gathered, or otherwise manufacture world state.

Personality affects realization, not task semantics, permissions, safety decisions, inventory accounting, or world authority.

## Context selectors

Fragment selection may be influenced by bounded authoritative context including:

- PersonalityProfile temperament, cadence, core value and humor
- mood
- nutrition and stamina
- current activity and mode
- task state
- combat state
- biome and weather
- nearby semantic features
- quest context
- recent relevant memory

Context must not grant new capabilities or bypass the normal task/permission systems.

## Required vocabulary coverage

The deterministic library must cover at minimum:

- summon, recall and dismissal
- follow, wait, guard and defend
- greetings and farewells
- task acknowledgement
- task start and progress
- task completion
- task failure and interruption
- task cancellation
- target lost or unreachable
- permission / claim denial
- missing materials
- inventory full
- gathering
- building and blueprint execution
- crafting
- inventory and equipment
- navigation
- combat and danger
- hunger, exhaustion and recovery
- ownership / lease state
- quests
- environmental observations
- autonomous activity selection, start, completion and abandonment

## Autonomous commentary

Autonomous behavior must be able to explain itself without inference. When the deterministic/autonomous system chooses an activity, the jigsaw receives the authoritative decision and may announce or summarize it. Dialogue must never be used as the mechanism that authorizes the activity.

## Repetition control

Track a bounded recent history of selected fragment variants/combinations per Companion. Prefer compatible alternatives before repeating the same realization. Repetition control must remain bounded and must not create an inference dependency.

## Inference escalation

Routine commands, task status, deterministic failures and ordinary autonomous chatter must not invoke inference merely to produce prose. Escalation is appropriate only when semantic interpretation or genuinely free-form conversation benefits from it.

The preferred execution architecture is:

OBSERVE -> deterministic affordances -> optional INFER/PLAN once -> VALIDATE -> deterministic primitives -> REPORT through jigsaw -> REPLAN only on completion, failure, interruption, or material world change.

The inference engine may select or propose validated capabilities; it cannot invent capabilities.

## Debugging and administration

Debug mode should expose semantic fragment/category IDs used to construct a line, for example:

`ACK_POSITIVE + TASK_START + GATHER + TARGET_ITEM + RETURN_OWNER`

This trace is diagnostic only and should not be shown to ordinary players.

## Acceptance criteria

The requirement is satisfied when:

1. The Companion can perform routine interaction and task reporting with the inference worker completely absent.
2. Personality profiles produce recognizably different realizations without changing factual content or authority.
3. Common task lifecycle and failure states have deterministic speech coverage.
4. Autonomous activities can announce/report their authoritative state without inference.
5. Repeated identical events demonstrate bounded phrase variation rather than a single endlessly repeated line.
6. Malformed/unavailable/timed-out inference falls back immediately to deterministic dialogue.
7. Debug mode can identify the semantic composition of a generated deterministic line.
8. Automated tests verify grammar assembly, substitution safety, factual-state preservation, personality selection, repetition control, and inference-fallback behavior.

## Release significance

This is part of the production Companion voice architecture, not optional polish. The Companion should remain recognizably the same character when the local inference worker is disabled or unavailable.