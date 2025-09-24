# Lock down Mongo

```
2025-09-12T14:55:28.631-04:00: Access control is not enabled for the database. Read and write access to data and configuration is unrestricted
```

---

# Tune Mongo

```
2025-09-12T14:55:28.631-04:00: For customers running MongoDB 7.0, we suggest changing the contents of the following sysfsFile
2025-09-12T14:55:28.631-04:00: vm.max_map_count is too low
```

Use something like this:

````
sudo sysctl -w vm.max_map_count=262144
```

on the command line when you start the db4e service.

---

# Edge Cases

- If upstream Monero or P2Pool is deleted, set downstream element's parent attribute to False.

---

# Wallet Changes

- Make sure P2Pool instances are updated and restarted

---

# Enable/Disable Db4E service

...

# Enter Wattage per Miner

I agree with you about electricity costs, for sure!!! I've added a note for a future feature to input wattage per miner and cost of power. Then I can calculate the electricity costs of the mining op and plot it against XMR earnings.

---

# Enable/Disable based on CPU utilization

Mine when the miner is idle, stop if it hits a CPU threshold.