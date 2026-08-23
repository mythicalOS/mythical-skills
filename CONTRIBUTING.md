# Contributing to mythical-skills

Thank you for considering a contribution. This is a content repository —
markdown skills, no build step — so contributing is mostly about writing well
within the framework's conventions.

## Before you write a skill

Read the authoring doctrine first: **`skills/skill-authoring/SKILL.md`**. It
defines what a skill is, how a `SKILL.md` is structured (frontmatter,
authority boundary, procedure, anti-patterns), and the writing rules —
including the two that most new contributions trip over:

- **Brand-free.** No product, vendor, or upstream brand names in skill
  content or in `SKILLS-INDEX.md`.
- **Project-agnostic.** Skills ship onto any consuming deployment. They keep
  the framework vocabulary (roles, rhythms, gates, routing, bus) but must not
  bind a single host or deployment ("runs on X", "in this project") or carry
  internal milestone tags.

## Adding or changing a skill

1. Author the content at `skills/<name>/SKILL.md` (one directory per skill).
2. Add or update the skill's row in `SKILLS-INDEX.md` — the index is the
   source of truth for existence, path, and status. Note that the index grants
   nothing: which roles may use a skill is the consuming deployment's
   role-policy decision, made outside this repo.
3. Run the content checks locally:

   ```bash
   scripts/check-project-agnostic.sh
   ```

   CI runs the same check plus a vocabulary denylist gate
   (`scripts/check-denylist.py`) over every tracked file. Both must pass.

4. Open a pull request. Keep it focused — one skill (or one coherent concern)
   per PR reviews best.

## Developer Certificate of Origin (DCO)

Every commit must be signed off. By signing off you certify the
[Developer Certificate of Origin 1.1](https://developercertificate.org/) — in short, that you
wrote the contribution or otherwise have the right to submit it under the project's licence.
There is no CLA, and you keep the copyright in what you write.

Sign off with `-s`:

```sh
git commit -s -m "your message"
```

That appends a trailer to your commit message:

```
Signed-off-by: Your Name <your.email@example.com>
```

Use your real name and an address you can be reached at. Anonymous and pseudonymous sign-offs
cannot be accepted.

To sign off commits you already made:

```sh
git rebase --signoff main       # or: git commit --amend -s   (for the last commit only)
```

## Authority is not granted here

A recurring review point: skill content may **describe** an authority model
(operator-only overrides, role escalation paths) but must never **grant**
authority — no skill can authorize publishing, routing, spawning, merging, or
overriding on its own. If your text reads as a permission grant, reword it as
procedure under externally supplied authority.

## Style

- The human principal is called the **operator** (see `README.md`
  §Vocabulary).
- Section names, status labels, and template headers that other skills consume
  are contracts — do not rename them casually; update every consumer if you
  must.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Report
concerns to dev@mythicalos.ai.
