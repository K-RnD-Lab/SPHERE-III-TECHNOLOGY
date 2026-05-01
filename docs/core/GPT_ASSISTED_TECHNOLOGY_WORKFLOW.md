# GPT-Assisted Technology Workflow

## Short answer

Yes, technology files from this repo can be sent directly into GPT chats.

The best format is a compact technical pack:

- starter study README
- relevant execution index section
- code, data, or tool notes
- implementation constraints
- expected output skeleton

## What to send into GPT

For one technology route, send:

1. the starter study `README.md`
2. `docs/core/T1_T3_RESEARCH_EXECUTION_INDEX.md`
3. any existing code, dashboard, data schema, or stack notes
4. the output you want: technical guide, dashboard documentation, scoring method, pipeline guide, or implementation note

If no skeleton exists yet, ask GPT to create one first.

## Recommended chat sequence

### Step 1: frame the technical route

Ask GPT:

```text
Read this technology route. Do not write the final output yet. First identify the use case, technical scope, inputs, outputs, stack, validation method, and likely repo artifact.
```

### Step 2: define verification needs

Ask GPT:

```text
List what must be verified before this technical recommendation is credible: docs, commands, data schema, version constraints, setup steps, tests, regeneration method, and maintenance risks.
```

### Step 3: draft the artifact

Ask GPT:

```text
Draft a repo-ready Markdown artifact. Include use case, technical scope, stack, implementation steps, validation checklist, limitations, maintenance notes, and next build step.
```

### Step 4: make it reusable

Ask GPT:

```text
Make this useful for someone who will actually implement or maintain it. Remove generic tool praise. Keep commands, decisions, tradeoffs, checks, and failure modes.
```

## Quality rules

Do not accept a GPT-written technology output unless it has:

- concrete use case
- technical scope
- stack or tool decision
- setup or implementation notes
- validation or regeneration method
- risks and limits
- next build step

Smooth technical explanation is not enough.

## Best first GPT-assisted test

Recommended first test:

- `T3-R1a` Study Registry Dashboard Template

Reason:

- it already connects all three spheres
- it has a visible public interface
- it can become the operational dashboard layer for the whole K R&D Lab system
