---
title: Architecture
---

# Introduction

This page is still being developed!

---

# Class Relationships

The diagrams below shows which classes are contained within another class and which classes contain a reference to an external class.

## App Replationships

![App Relationships](/images/App-Relationships.png)

## Server Relationships

![Server Relationships](/images/Server-Relationships.png)

---

# Mining Data Origins

**Db4E** creates records in a SQLite database based on events that are discovered in the *P2Pool* log file and by querying the *P2Pool* API. See the [schema page](/pages/Schema.html) for detailed information.
