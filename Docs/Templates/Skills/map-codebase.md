# Map Codebase Skill (Template)

<!-- ANNOTATION: The map-codebase skill automates the scan-classify-update
     pipeline for populating area maps and symbol pages in the wiki. It
     replaces manual codebase exploration with a systematic scan that uses
     Glob/Grep/Read (LLM reasoning needed for classification -- Bash alone
     cannot determine which subsystem a class belongs to).

     This skill is ALWAYS included for game-development profiles and
     conditionally included for software-development profiles when Pattern F
     (Codebase Mapping) is active. -->

<!-- QUALITY: Must demonstrate the scan -> classify -> update pipeline.
     Must be re-runnable and non-destructive (preserve manual notes).
     Must handle empty codebases gracefully. Must use only Glob/Grep/Read
     (no Bash). SKILL.md under 500 lines. -->

## Progressive Disclosure Structure

```
map-codebase/
  SKILL.md                    # Core instructions (< 500 lines)
  references/
    classification-guide.md   # Domain-specific classification rules (optional)
```

<!-- ANNOTATION: No scripts/ directory -- this skill relies on LLM reasoning
     for classification, not deterministic scripts. The LLM reads headers,
     identifies patterns (UCLASS, [SerializeField], decorators, etc.), and
     classifies each module/class into the right area. A script cannot do
     this because classification requires understanding inheritance, naming
     conventions, and domain semantics. -->

## Example: Map Codebase Skill (`.claude/skills/map-codebase/SKILL.md`)

````markdown
---
name: map-codebase
description: >
  Scan the project source tree and populate area maps with real class and
  module data. Use when the user says "map the codebase", "scan source files",
  "populate area maps", "update area maps", "what classes are in my project",
  or "/map-codebase". Also use after major refactors that add or move files.
  Do NOT use for exploring a single file or answering "where is X" (use the
  explorer for that). Do NOT use for code review or debugging.
context: fork
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
metadata:
  version: 1.0.0
---

<!-- ANNOTATION: Frontmatter design decisions:
     - context: fork (scanning is token-heavy; isolate from main context)
     - allowed-tools: Glob/Grep for discovery, Read for inspection,
       Write/Edit for updating area pages. No Bash -- all scanning is
       tool-based so the LLM can reason about classification.
     - description: 6 trigger phrases, 2 negative triggers
     VARIATION: For very large codebases (1000+ files), consider adding
     a max-files-per-area cap to prevent context exhaustion. -->

## Important: Non-Destructive Updates

<!-- ANNOTATION: This is the most critical constraint. Users may have
     added manual notes, architectural context, or decision records to
     their area pages. The skill must preserve all of that. -->

This skill is re-runnable and non-destructive:
- Preserve all manually written prose, notes, and context in area pages
- Only update the "Key Files" and "Key Classes" sections
- Update metadata (Last Updated date, Confidence level)
- If an area page has content you did not generate, leave it intact
- If a class was previously listed but no longer exists, mark it
  as "(removed)" rather than deleting the entry

## Procedure

### Step 1: Discover Modules

<!-- VARIATION:
     UE/C++: Glob for *.Build.cs to find modules, then enumerate .h/.cpp
     Unity/C#: Glob for *.asmdef to find assemblies, then enumerate .cs
     General: Glob for project structure markers (package.json, go.mod,
              Cargo.toml, pyproject.toml, etc.) then enumerate source files -->

Scan the source tree to identify all modules or packages:

**Unreal Engine (C++)**:
```
Glob: Source/**/*.Build.cs        -> module list
Glob: Plugins/**/Source/**/*.h    -> plugin headers
Glob: Source/**/*.h               -> project headers
Glob: Source/**/*.cpp             -> project sources
```

**Unity (C#)**:
```
Glob: **/*.asmdef                 -> assembly list
Glob: Assets/**/*.cs              -> project scripts
Glob: Packages/**/*.cs            -> package scripts
```

**General Software**:
```
Glob: **/package.json             -> Node packages
Glob: **/go.mod                   -> Go modules
Glob: **/Cargo.toml               -> Rust crates
Glob: **/pyproject.toml           -> Python packages
Glob: src/**/*.<ext>              -> source files
```

If no source files are found, report "Empty or unrecognized codebase
structure" and exit gracefully.

### Step 2: Extract Declarations

<!-- VARIATION:
     UE/C++: Grep for UCLASS, USTRUCT, UENUM, UINTERFACE; Read headers
             for inheritance (public AActor, public UActorComponent, etc.)
     Unity/C#: Grep for class declarations, MonoBehaviour, ScriptableObject
     General: Grep for class/struct/interface/type declarations per language -->

For each source file, extract key declarations:

**Unreal Engine**: Grep for reflection macros
```
UCLASS     -> class declarations (read header for parent class)
USTRUCT    -> struct declarations
UENUM      -> enum declarations
UINTERFACE -> interface declarations
```

**Unity**: Grep for class patterns
```
class.*MonoBehaviour      -> component scripts
class.*ScriptableObject   -> data assets
class.*Editor             -> editor extensions
```

**General**: Grep for language-appropriate declaration patterns.

For each declaration, note:
- Class/type name
- Parent class (if applicable)
- File path
- Module/package it belongs to

### Step 3: Classify into Areas

<!-- ANNOTATION: This is where LLM reasoning is essential. A script
     cannot determine that "UProjectileDamageExecution" belongs to the
     combat area based on its inheritance from UGameplayEffectExecutionCalculation
     and its naming pattern. The LLM reads the header, sees the GAS
     inheritance, the "Damage" in the name, and classifies correctly. -->

Read the existing area pages (Docs/Areas/) to understand the current
area taxonomy. Classify each discovered class into an area based on:

1. **Inheritance chain**: Parent class strongly indicates area
2. **Naming patterns**: Prefixes/suffixes that match area vocabulary
3. **File location**: Directory structure often mirrors area boundaries
4. **Include dependencies**: What other systems does this class reference

<!-- VARIATION: Classification heuristics by domain:
     UE/C++:
       combat = GAS (GameplayAbility, GameplayEffect, AbilityTask),
                damage types, hit detection, projectiles
       networking = Replication, RPC, NetSerialize, authority checks
       input = Enhanced Input, InputAction, InputMappingContext
       audio = SoundCue, AudioComponent, MetaSound
       ui = UUserWidget, UCommonActivatableWidget, Slate
       ai = BehaviorTree, BTTask, Blackboard, AIController
     Unity/C#:
       gameplay = MonoBehaviour game logic, state machines
       networking = Mirror/Netcode components, NetworkBehaviour
       ui = Canvas, UI Toolkit, UGUI components
       audio = AudioSource, AudioMixer
     General:
       api = route handlers, controllers, middleware
       data = models, repositories, database access
       ui = components, views, templates
       infra = config, logging, deployment -->

If a class does not fit any existing area, note it as "unclassified"
and mention it in the summary. Do not create new areas unless 3+
classes share a clear theme not covered by existing areas.

### Step 4: Update Area Pages

For each area page in Docs/Areas/:

1. Read the current content
2. Find the "Key Files" or "Key Classes" section
3. If the section contains a placeholder ("Populate after first codebase
   scan" or similar), replace it with the discovered data
4. If the section already has data, merge: add new entries, keep
   existing entries that still exist on disk, mark removed entries
5. Update the metadata:
   - `Last Updated: YYYY-MM-DD`
   - `Confidence: high` (if scan found matching files) or
     `Confidence: medium` (if classification was ambiguous)
6. Preserve all other sections (overview, architectural notes, etc.)

Format for Key Files sections:
```markdown
## Key Files

| File | Type | Description |
|------|------|-------------|
| Source/Combat/Abilities/GA_MeleeAttack.h | UCLASS (UGameplayAbility) | Melee attack ability |
| Source/Combat/Effects/GE_ApplyDamage.h | UCLASS (UGameplayEffect) | Base damage effect |
```

### Step 5: Create Symbol Pages (Optional)

<!-- ANNOTATION: Symbol pages are for central classes that span multiple
     areas or are frequently referenced. Do not create a symbol page for
     every class -- only for the 5-10 most important ones. -->

For classes that appear central to the architecture (referenced by many
other classes, or serving as base classes for an entire subsystem):

1. Create `Docs/Symbols/<ClassName>.md` if it does not exist
2. Include: file path, parent class, key properties/methods, which
   areas reference it, dependencies
3. Keep symbol pages concise (< 50 lines)

Skip this step if fewer than 20 classes were discovered.

### Step 6: Update Index

Update `Docs/index.md` to include any new area or symbol pages created.
Do not modify entries for pages you did not create or update.

## Empty Codebase Handling

If Step 1 finds no source files:
- Report: "No source files found matching expected patterns for this
  project type. Checked: [list of glob patterns tried]"
- Suggest: "If your source files are in a non-standard location,
  tell me the path and I will scan there."
- Do NOT modify any area pages
- Exit gracefully

## Output Format

After completing all steps, produce a summary:

```markdown
## Codebase Map Summary

Scanned: YYYY-MM-DD HH:MM

### Modules Discovered
| Module | Files | Headers | Sources |
|--------|-------|---------|---------|
| CombatSystem | 24 | 12 | 12 |
| Networking | 18 | 9 | 9 |

### Classification Results
| Area | Classes Found | New | Updated | Confidence |
|------|--------------|-----|---------|------------|
| combat | 15 | 15 | 0 | high |
| networking | 8 | 8 | 0 | high |
| ui | 4 | 4 | 0 | medium |

### Unclassified
- FMyUtilityClass (Source/Utils/MyUtility.h) -- does not fit existing areas

### Symbol Pages Created
- AProjectCharacter (Docs/Symbols/AProjectCharacter.md)

### Area Pages Updated
- Docs/Areas/combat.md (15 classes added)
- Docs/Areas/networking.md (8 classes added)
```
````

<!-- VARIATION: For Unreal Engine projects, the classification-guide.md
     in references/ should include:
     - GAS class hierarchy (UGameplayAbility -> UGA_*, UGameplayEffect -> UGE_*)
     - Replication markers (GetLifetimeReplicatedProps, DOREPLIFETIME)
     - Enhanced Input class patterns
     - Common base classes and what areas they indicate
     For Unity projects: MonoBehaviour subtypes, assembly definitions,
     namespace conventions. -->

## Example Reference: `references/classification-guide.md`

<!-- ANNOTATION: This file is loaded on demand when the skill needs
     help classifying ambiguous classes. Keep it under 200 lines.
     Domain-specific content only. -->

```markdown
# Classification Guide

## Unreal Engine Classification Heuristics

### Combat Area
- Parent: UGameplayAbility, UGameplayEffect, UAbilityTask
- Keywords: Damage, Attack, Ability, Combo, Hit, Projectile
- Macros: GAMEPLAYATTRIBUTE_REPNOTIFY, ATTRIBUTE_ACCESSORS

### Networking Area
- Functions: GetLifetimeReplicatedProps, ServerRPC, ClientRPC, MulticastRPC
- Macros: DOREPLIFETIME, UPROPERTY(Replicated)
- Keywords: Net, Replicated, Authority, Server, Client

### Input Area
- Parent: UInputAction, UInputMappingContext
- Keywords: Input, Binding, Action, Axis, EnhancedInput

### Audio Area
- Parent: USoundCue, UAudioComponent
- Keywords: Sound, Audio, Music, SFX, MetaSound

### UI Area
- Parent: UUserWidget, UCommonActivatableWidget
- Keywords: Widget, HUD, Menu, UI, Slate, UMG
```

<!-- QUALITY: Validation checklist for the generator:
     - [ ] SKILL.md under 500 lines
     - [ ] Description includes 6+ trigger phrases
     - [ ] Description includes 2+ negative triggers
     - [ ] context: fork specified
     - [ ] allowed-tools: Read, Write, Edit, Glob, Grep (no Bash)
     - [ ] Non-destructive update behavior documented
     - [ ] Empty codebase handling documented
     - [ ] Output format specified with summary table
     - [ ] Classification heuristics are domain-specific
     - [ ] Step 4 preserves manual notes in area pages
     - [ ] No README.md inside the skill folder
     - [ ] references/ contains classification guide (not in SKILL.md)
-->

<!-- ANTI-PATTERN: Do not load all source files into context at once.
     Use Glob to discover file paths, Grep to extract declarations,
     and Read only the headers/files needed for classification. A
     project with 500 source files would exhaust context if all were
     read. Scan patterns first, read selectively. -->

<!-- ANTI-PATTERN: Do not invent new area pages that are not in the
     existing wiki structure. If the wiki has 5 areas, classify into
     those 5. Only suggest new areas in the summary output for the
     user to decide. -->

<!-- ANTI-PATTERN: Do not run this skill automatically on every session
     start. It is meant to be run explicitly or when area pages have
     stale/placeholder content. The orchestrator may check area freshness
     and suggest running it, but should not auto-trigger it. -->
