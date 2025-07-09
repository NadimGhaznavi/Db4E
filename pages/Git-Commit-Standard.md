---
title: Git
layout: default
---

# Introduction

This document outlines a specification for adding human- and machine-readable meaning to commit messages. It is based on the [Conventional Commits Specification](https://www.conventionalcommits.org/) and has been adopted by [Db4E](https://github.com/NadimGhaznavi/Db4E), the [Database 4 Everything](https://db4e.osoyalce.com/) project.

This convention dovetails with the [Semantic Versioning](http://semver.org/) specification by describing the features, fixes, and breaking changes made in commit messages.

---

# Imperative Mood

Write messages like a command:

* **Good:** `Add user authentication`
* **Bad:** `Added user authentication` or `Adding user authentication`

---

# Limit Subject to 50 Chars

Keep it short and sweet, concise enough to read in one glance.

---

# Multi-Line Format

Separate the subject from the body with a blank line. Sample message:

```
Add support for remote monerod deployment

Refactored the installer to handle remote nodes by:
- Passing SSH keys securely
- Adding retries on connection failures
- Documenting usage in the README
```

---

# Limit Lines to 72 Chars

This improves readability in terminals and git tools.

---

# Why, not Just What

The *diff* shows *what* changed. The message should give context on *why*.

---

# Use Bullets or Paragraphs

Using bullets or paragraphs helps organize details, especially for complex changes.

---

# Reference Issues, Tickets, or PRs

Where applicable, include reference numbers to project issues, tickets or PRs. For example:

```
fix: race condition on startup (#42)
```

---

# Prefix Categories

Use the following prefixes:

- `feat:` A new feature.
- `fix:` A bug fix.
- `docs:` Documentation only changes.
- `style:` Formatting changes, not code changes.
- `refactor:` Code changes that neither fixes a bug nor adds a feature.
- `test:` Adding or refactoring Tests.
- `chore:` Build process or auxiliary tool changes.

For example:

```
feat: add support for remote monerod deployment

This adds the ability to deploy monerod nodes on remote machines
via SSH, including secure key handling and connection retries.
```

---

# Links 

* [Conventional Commits](https://www.conventionalcommits.org/)
* [Semantic Versioning](https://semver.org/)