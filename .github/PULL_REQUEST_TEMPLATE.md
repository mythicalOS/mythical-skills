<!--
Thanks for contributing. Please read CONTRIBUTING.md if you have not already:
../CONTRIBUTING.md
-->

## What this changes

<!-- Which skill does this affect? Describe the procedure before and after. -->

## Why this approach

<!-- What alternatives did you consider and why did you reject them? -->

## Related issue

<!-- e.g. Closes #123. Open an issue first for anything beyond an obvious fix. -->

## How this was verified

<!-- The checks you ran and their output. "Checks pass" without the command is not evidence. -->

```
```

## Checklist

- [ ] Every commit is signed off (`git commit -s`) — see the DCO section of CONTRIBUTING.md
- [ ] One concern only; unrelated changes are in a separate pull request
- [ ] A new or renamed skill has both its `skills/<name>/SKILL.md` and its `SKILLS-INDEX.md` row
- [ ] `scripts/check-frontmatter.sh` and `scripts/check-project-agnostic.sh` pass
- [ ] The content stays deployment-agnostic — no consuming-project names, host bindings, or internal milestone tags
- [ ] A new frontmatter key is a deliberate schema change, extending the closed set in `scripts/check-frontmatter.sh` in the same commit
- [ ] CI is green
- [ ] This is **not** a security fix — if it is, stop and follow [SECURITY.md](../SECURITY.md) instead
