---
title: Git Branching Strategy
layout: default
---

# Diagram

In the example below, the current project release is v1.2.3.

  <pre class="mermaid">
    gitGraph
    commit id: " "
    branch dev
    checkout dev
    commit id: "  "
    branch feature/foo
    checkout feature/foo
    commit id: "Add foo feature"
    commit id: "Add foo tests"
    checkout dev
    merge feature/foo
    commit id: "Merge feature: foo"

    branch release/v1.2.4
    checkout release/v1.2.4
    commit id: "Update toml version"  tag: "v1.2.4"
    checkout dev
    merge release/v1.2.4
    checkout main
    merge release/v1.2.4

    commit id: "   "
    checkout dev
    commit id: "    "
  </pre>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({ startOnLoad: true });
  </script>

---

# Branching Strategy

* **main**: Stable production-ready code only. Every commit here is a release candidate.
* **development**: Integration branch for feature branches before merging into main.
* **feature/xxx**: Short-lived branches created from development or main for individual features or fixes.
* **release/xxx**: Branches created from development when preparing for a release, for final testing and fixes.
* **bugfix/xxx**: Branches created from main to fix critical bugs on production releases.

---

# Dev work in Dev

All work happens within a *development* branch.

The dev branch already exists.

```
git branch | grep dev
```

Should output:

```
dev
```

---

# Feature Branch off Dev

A new branch is created off the *development* branch to house the feature.

```
git checkout dev
git pull origin dev
git checkout -b feature/foo
```

The developer switches to the *feature/foo* branch where the development work is done.

```
git checkout feature/foo
```

Once the work is complete, the changes are committed into the *feature/foo* branch.

```
git add . -v
git commit -m "New foo feature"
git push origin feature/foo
```

# Merge Feature Branch into Dev

Finally, the *feature/foo* branch is merged into the *dev* branch.

```
git checkout dev
git pull origin dev
git merge feature/foo -m "New foo feature"
git push origin dev
```

---

# Release Branch

With the project version at *v1.2.3*, a *release/v1.3.0* branch is created off the *dev* branch.

```
git checkout dev
git pull origin dev
git checkout -b release/v1.3.0
git push origin release/v1.3.0
```

Update the `pyproject.toml` and increase the version to 1.3.0.

```
git add pyproject.toml
git commit -m "Bump version to v1.3.0"
git push origin release/v1.3.0
```

# Merge Release Branch into Main

```
git checkout main
git merge release/v1.3.0 -m "Release v1.3.0"
git tag -a v0.17.5 -m "Release v0.17.5"
git push origin main --tags
```

---

# Merge Release Branch into Dev

```
git checkout dev
git pull origin dev
git merge release/v1.3.0 -m "Sync release v1.3.0 back into dev"
git push origin dev
```

---

# Bug Fixes

The same process is used for bug fixes, except the branch name is different. The branch name would then be *bugfix/v1.3.1*.

