# Team Workflows

## Overview

Spec-driven development changes how teams collaborate, not just how individuals write code.
This guide covers the team-level workflows: sprint planning, implementation PRs, end-of-sprint
sync, and onboarding a new feature from an existing tracker. These workflows connect the
individual story lifecycle (covered in [01-process-guide.md](01-process-guide.md)) to the
team's shared cadence.

---

## Workflow 1: Sprint Planning

Sprint planning produces a baselined set of stories with implementation tasks, committed to
via a Spec PR before any code is written.

### The Spec PR pattern

A Spec PR contains only spec file changes — story files with `## Implementation Tasks` added.
No source code, no infrastructure. Reviewing a plan is faster than reviewing code; this makes
the plan reviewable.

```
Branch:   spec/<feature-slug>-sprint-<N>
Title:    [SPEC] Feature 101 — Sprint 2 implementation plans
Contents: Story files with ## Implementation Tasks sections added
```

### Step-by-step

**Before the planning session:**
1. Developer reads the upcoming stories from `tasks.md`
2. Developer reviews the feature's `design.md` to refresh context
3. Developer opens Kiro and attaches the relevant story file

**During the planning session (with Kiro):**
```
I'm planning Sprint 2 for Feature 101. Let's discuss the implementation
approach for story A3 (RBAC).

Context from design.md:
- DEC-003 chose FastAPI Depends for middleware
- CurrentUser from A2 provides the role claim

I'm thinking require_role(minimum_role) as a factory function.
What's the right shape for the Role enum and hierarchy?
```

4. Discuss and agree on the approach
5. Kiro adds `## Implementation Tasks` to the story file
6. Repeat for each story in the sprint

**After the planning session:**
7. Commit the story files with impl tasks: `git add .kiro/specs/`
8. Open a Spec PR on `spec/<feature-slug>-sprint-N`
9. Reviewers check the plan (see review checklist below)
10. Merge → sprint is baselined

### What reviewers check in a Spec PR

- [ ] Are implementation tasks comprehensive enough to execute without ambiguity?
- [ ] Is the approach aligned with the decisions in `design.md`?
- [ ] Is there a Validation task group in every story?
- [ ] Are dependencies between tasks correctly ordered?
- [ ] Is the effort estimate still realistic given the task breakdown?
- [ ] Are any acceptance criteria not covered by tasks?

### What a Spec PR does NOT contain

- Source code (`.py`, `.tf`, `.ts` files) — those belong in an Implementation PR
- Changes to `requirements.md` or `design.md` (mid-sprint scope changes need a separate discussion)
- Passing CI quality gates (there's no code to lint)

---

## Workflow 2: Implementation PR

An Implementation PR contains the deliverable code, checked off tasks, and any story file
updates required by what was built.

```
Branch:   story/<tracker-id>-<slug>
Title:    [ADO-12303] Role-based access control — FastAPI require_role dependency
Contents: Source code, tests, infra, ADRs (if any), updated story file
```

### Commit convention

Every commit on a `story/*` branch should carry a work-item trailer:

```
Add require_role dependency and Role enum

Implements task 1 and task 2 of story A3 (RBAC).

Work-Item: ADO-12303
Story: A3
```

The `work-item-link-check` CI workflow reads this trailer to validate traceability.

### Step-by-step

1. Create the branch: `git checkout -b story/ADO-12303-rbac`
2. Tell Kiro which story you're executing:
   ```
   I'm implementing story A3 (RBAC, ADO-12303). The impl tasks are already
   in the story file from the Sprint 2 Spec PR. Let's start with Task 1.
   ```
3. Kiro writes code, checks off task boxes as work completes
4. After all tasks (including Validation) are checked:
   - Update `state: Active` → `state: Done` in the story front-matter
5. Commit with the work-item trailer
6. Open the PR
7. CI runs: spec-integrity, work-item-link-check, code-quality, terraform-plan
8. `pr-completeness-review` posts an advisory checklist (advisory — not a blocker)
9. Human reviewer approves
10. Merge

### What reviewers check in an Implementation PR

The `pr-completeness-review` workflow posts a machine-generated checklist covering:
- All implementation tasks checked off
- Story state agrees with task checkboxes
- ADR present if design.md was changed
- Test files touched

Reviewers then evaluate what the machine cannot:
- Do the tests actually exercise the acceptance criteria?
- Does the implementation match the design decision, or is there a deviation to record?
- Is the code safe and secure?

---

## Workflow 3: End-of-Sprint Sync

At the end of each sprint, sync story states to the tracker and check for drift.

### Sync completed stories

1. Attach the sync playbook: type `#work-item-sync-playbook` in the Kiro chat
2. Tell Kiro:
   ```
   Sync all Done stories for Feature 101 to the Azure DevOps tracker.
   ```
3. Kiro reads each Done story, computes the fields to update, and shows you the payload
4. You approve story by story (or batch-approve if everything looks right)
5. Kiro calls the tracker API and updates each work item
6. Kiro updates `lastSync` timestamps in the story files and `work-item-map.yaml`

### Check for drift

Someone may have edited the tracker directly during the sprint:

```
Check for drift between the tracker and our story files for Feature 101.
Show me any fields that differ since the last sync.
```

Kiro reads both sides and shows a diff table:

```
Story A3 — drift detected:
  Field       | Tracker         | Story file
  ------------|-----------------|------------
  state       | Active          | Done
  effort      | 5               | 4
  
Accept tracker value, overwrite tracker, or skip? (for each field)
```

### Update tasks.md

After syncing, update the sprint checklist:

```
Update tasks.md for Feature 101 to mark the Sprint 2 stories as complete.
```

---

## Workflow 4: Feature Onboarding from Tracker

When an existing feature already exists in the tracker and you want to bring it into Kiro's
spec structure, pull rather than recreate.

### When to use this

- Team adopting Kiro mid-project, with features already planned in ADO/GitHub
- Importing a feature designed in a different tool
- Picking up work from a team that didn't use Kiro

### Step-by-step

```
Pull Feature ADO-201 from the Azure DevOps tracker into Kiro specs.

The feature is called "Project CRUD API" and has 5 child stories.
```

Kiro will:
1. Read the Feature work item and all child Story work items from the tracker
2. Create the spec folder structure (`.kiro/specs/201-project-crud/`)
3. Generate `requirements.md` from the Feature description
4. Generate story files from child Story work items
5. Populate `work-item-map.yaml` with real tracker IDs and state
6. Set `lastSync` timestamps

You then:
7. Review the generated specs and fill any gaps (design.md, story context, acceptance criteria)
8. Raise a Spec PR to baseline the specs before planning implementation tasks

---

## Workflow 5: Handling Common Situations

### Mid-sprint scope change

**Situation:** A story needs to shrink, grow, or split during the sprint.

```
Story A3 is larger than we thought. Let's split the Role enum work
into a separate story A5 and move A5 to Sprint 3.

Update A3 to reflect the reduced scope, create A5 for the remaining
work, update tasks.md, and update capacity in work-item-map.yaml.
```

Kiro updates the files; you raise a narrow Spec PR documenting the change.

### Technical debt discovered during implementation

```
I found a performance issue in the JWKS cache (story A2) while
implementing A3. It's not a blocker for this sprint but needs to
be fixed.

Create a debt story A5 for the cache optimization, add it to
work-item-map.yaml as deferred_to_next_pi for now.
```

### Cross-team dependency blocked

When a story is blocked on another team:

1. Update the story front-matter: `state: New` with a `# BLOCKED: waiting on team-X to deliver API contract`
2. Record in `tasks.md`: checkbox stays unchecked with a blocker note
3. Kiro can create a tracker work item to track the dependency if needed

### Hotfix (bypassing the spec flow)

For production emergencies, bypass the spec flow and reconcile after:

1. Fix directly on a `hotfix/<slug>` branch with a minimal commit
2. Merge via normal PR after emergency review
3. After the incident, run:
   ```
   We merged hotfix/ADO-12399-auth-token-expiry without a story file.
   Help me create a retroactive story file and record it in work-item-map.yaml.
   ```

---

## Workflow 6: PI Boundary Transition

At the end of a PI, roll incomplete work forward and set up the next PI.

```
PI 1 is ending. Let's do the PI close:

1. Which stories are Done vs incomplete?
2. Roll incomplete stories to PI 2 as carryover
3. Update sprint aliases in the sync playbook for PI 2
4. Refresh product-overview.md to reflect what actually shipped vs what was planned
5. Update deferred_to_next_pi in each work-item-map.yaml
```

Kiro reads all story states, computes carryover, and proposes the updates for your approval.

---

## PR Naming Reference

| Workflow | Branch prefix | PR title format |
|----------|--------------|-----------------|
| Sprint planning | `spec/<feature-slug>-sprint-<N>` | `[SPEC] Feature 101 — Sprint 2 plans` |
| Implementation | `story/<tracker-id>-<slug>` | `[ADO-12303] RBAC require_role dependency` |
| Hotfix | `hotfix/<tracker-id>-<slug>` | `[HOTFIX] ADO-12399 auth token expiry fix` |
| Epic/feature planning | `spec/<epic-slug>-pi-<N>` | `[SPEC] Epic 1 — PI 2 feature decomposition` |

---

## Team Health Checks

Run these periodically to keep specs and tracker in sync:

```
Run the spec integrity check and tell me what it finds.
```

```
Show me all stories across Feature 101 and 301 that are Done
but haven't been synced to the tracker yet.
```

```
Which stories in the current sprint have unchecked validation tasks?
```
