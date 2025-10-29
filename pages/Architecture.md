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

---

# Data Abtraction Layer

**Db4E** has a number of database related classes as outlined in the table below.

Module       | Description
-------------|-----------------
SQLDb        | Owns the SQLite database file, database connection and cursor.
BaseDb       | Virtual class.
DeplDb       | Owns the *deployment* tables and provides deployment related functionality
MiningDb     | Owns the *mining* tables and provides mining related functionality
OpsDb        | Owns the *operations* tables and provides operations related functionality

