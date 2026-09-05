# FTB Quest Authoring Note

The prototype does not ship guessed FTB Quest SNBT.

Launch the pack once and let the installed FTB Quests version establish its native data/config
structure. Author the first chapter in-game (or export a known-good SNBT baseline) and then place
the validated quest data into the pack overrides for the next release.

This avoids creating an import package that looks complete but fails because of stale quest syntax.
