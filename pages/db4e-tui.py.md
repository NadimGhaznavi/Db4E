---
title: Console Application
---

# Console Application

The `db4e` command launches a unified Monero XMR mining dashboard for deployment, operation and real-time analytics. It's built using the [Textual](https://textual.textualize.io/) Rapid Application Development framework and offers a modern TUI experience right from your terminal.

![Screenshot of db4e-gui.sh](/images/db4e-gui.png)

---

# Architecture Highlights

Db4E’s Textual UI is structured around a clean, reactive design pattern:

* 🧩 **TopBar**: Persistent UI element displaying mining status, errors, and global actions.
* 🔀 **ContentSwitcher**: Central dynamic view container that swaps panes based on user interaction.
* 📂 **PaneMgr**: Custom class managing creation, update, and state of views/panes.
* 📝 **FormPanes**: Interactive config forms for components like Monerod, P2Pool, and XMRig.
* 📊 **Live Metrics Pane** (coming soon): Will include Plotext-powered mining graphs and analytics.

The UI is tightly integrated with the underlying service and MongoDB backend to provide accurate, real-time feedback.

---

# Launch the App

After installation:

```shell
pip install db4e
db4e
```






