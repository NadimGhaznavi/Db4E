---
title: Installing MongoDB on Debian
---

# Repository Public Key

Install gnupg and curl if they are not already available:

```
sudo apt-get install gnupg curl
```

To import the MongoDB repository public GPG key, run the following command:

```
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
   --dearmor
```

---

# Repository List File

Create the list file for Debian 12 (Bookworm):

```
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] http://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
```

---

# Reload the Package DB

Issue the following command to reload the local package database:

```
sudo apt-get update
```

---

# Install MongoDB

You can install either the latest stable version of MongoDB or a specific version of MongoDB.

```
sudo apt-get install -y mongodb-org
```

---

# Run MongoDB

---

## ulimit Considerations

Most Unix-like operating systems limit the system resources that a process may use. These limits may negatively impact MongoDB operation, and should be adjusted. See [UNIX ulimit Settings for Self-Managed Deployments](https://www.mongodb.com/docs/manual/reference/ulimit/) for the recommended settings for your platform.

---

## Start MongoDB

You can start the mongod process by issuing the following command:

```
sudo systemctl start mongod
```

If you receive an error similar to the following when starting mongod:

```
Failed to start mongod.service: Unit mongod.service not found.
```

Run the following command first:
```
sudo systemctl daemon-reload
```

Then run the start command above again.

---

## Stop MongoDB

As needed, you can stop the mongod process by issuing the following command:
```
sudo systemctl stop mongod
```

---

## Restart MongoDB

You can restart the mongod process by issuing the following command:
```
sudo systemctl restart mongod
```

You can follow the state of the process for errors or important messages by watching the output in the /var/log/mongodb/mongod.log file.

---

## MongoDB Status

```
sudo systemctl status mongod
```

You can optionally ensure that MongoDB will start following a system reboot by issuing the following command:
```
sudo systemctl enable mongod
```

---

# Links

* [MongoDB Homepage](https://www.mongodb.com)
  * [Official Install Docs](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-debian/)
  * [UNIX ulimit Settings for Self-Managed Deployments](https://www.mongodb.com/docs/manual/reference/ulimit/)







