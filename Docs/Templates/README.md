# Templates

Annotated reference implementations for the component-generator agent.

## How Templates Work

Templates are NOT fill-in-the-blank. They are complete, working examples of each
component type, annotated with HTML comments that explain design decisions,
variation points, and quality criteria. The component-generator reads them as
guidance and composes content adapted to the user's GENESIS.md and ARCHITECTURE.md.

## Annotation Format

Templates use HTML comments for annotations:

```markdown
<!-- ANNOTATION: Explanation of why this section exists and how to adapt it -->
```

Common annotation types:
- `ANNOTATION:` -- General guidance for this section
- `VARIATION:` -- How this section changes across domains
- `ANTI-PATTERN:` -- What NOT to do, with explanation
- `QUALITY:` -- Validation criteria the generator should check
- `EXAMPLE:` -- Alternative phrasing or content for a different domain

## Directory Structure

```
Templates/
  README.md              # This file
  Core/                  # 14 core component references (always generated)
  Optional/              # 10 optional component references (generated when applicable)
  Agents/                # 9 agent templates with full TOML schemas
  Skills/                # 5 skill templates with progressive disclosure
```

## How the Component-Generator Uses Templates

1. Reads the relevant template for the component being generated.
2. Uses annotations to understand intent and variation points.
3. Adapts content based on GENESIS.md (user answers) and ARCHITECTURE.md (design).
4. Validates output against the QUALITY annotations.
5. Does NOT copy templates verbatim -- every generated file should feel tailored.

## Contributing New Templates

1. Write a complete, working example of the component.
2. Add HTML comment annotations throughout explaining design decisions.
3. Include at least one VARIATION note showing a different domain.
4. Include at least one ANTI-PATTERN note.
5. Include QUALITY criteria the validator can check.
6. Keep templates under 300 lines (longer templates are harder to use as guidance).
7. Use ASCII-only characters.
