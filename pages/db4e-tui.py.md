---
title: Console Application
---

# Console Application

The `db4e` command launches a unified Monero XMR mining dashboard for deployment, operation and real-time analytics. It's built using the [Textual](https://textual.textualize.io/) Rapid Application Development framework and offers a modern TUI experience right from your terminal.

![Screenshot of Db4E](/images/db4e-tui.png)

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

# Screenshots

![Initial Setup Screen](/images/initial-setup.png)

![Screenshot of Db4E installer](/images/db4e-tui-installer.png)

![Monero Configuration](/images/monerod-config.png)

![Monero Remote Configuration](/images/monerod-remote-config.png)

![P2Pool Config](/images/local-p2pool-config.png)

![P2Pool Remote Configuration](/images/p2pool-remote-config.png)

![XMRig Configuration](/images/xmrig-config.png)

![Monero Daemon Logs](/images/monerod-logs.png)

![P2Pool Logs](/images/p2pool-logs.png)

![XMRig Logs](/images/xmrig-logs.png)

![Console Log](/images/console-log.png)

![Miner Analytics](/images/miner-analytics.png)

![Pool Hashrates](/images/pool-hashrates.png)

![Runtime Log](/images/runtime-log.png)

![Start / Stop Log](/images/start-stop-log.png)

![Runtime Log](/images/runtime-log.png)

![P2Pool Hashrate](/images/p2pool-hashrate.png)

![P2Pool Shares Found](/images/p2pool-shares-found.png)

![XMRig Hashrate](/images/xmrig-hashrate.png)

![Chain Blocks Found](/images/chain-blocks-found.png)

![Chain Hashrates](/images/chain-hashrates.png)