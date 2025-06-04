---
title: Codebase Architecture
layout: default
---

# Infrastructure Modules

Module      | Description
------------|--------------------
Db4eConfig  | This module is responsible for loading *db4e* application settings from an YAML file.
Db4eDb      | This module is responsible for all MongoDb operations.
Db4eGit     | This module is responsible for pushing files up to GitHub.
Db4eLog     | This module is responsible for managing logging of the application.

# Mining Modules

Module               | Description
---------------------|--------------------------------------
MiningDb             | Accepts mining specific DB commands and then uses the Db4eDb module to execute them.
P2Pool               | Monitors the P2Pool log, queries the API and creates corresponding events in MongoDb using the MiningDb module.
MiningReports        | Parses the reports definition files, generates CSV, Javascript and GitHub markdown files and publishes to GitHub Pages.

# JavaScript

Javascript files for the different report types have been written. These render the CSV data into plots such as bar charts and area graphs using the Javascript Apexchars library.

