#  sohel.dependency_checker

A custom, cross-platform Ansible module to validate **service, port, and ping dependencies** before performing any critical operations like restarting a service, applying system updates, or triggering deployments.

---

## ✅ Features

- ✔️ **Cross-platform** support: works on Linux & Windows
-  **Retry mechanism** with delay per dependency
- ️ **Auto-fix failed services** (optional)
- 蝹 **Optional logging** to file with timestamps
-  **Detailed results per dependency**
- ♻️ Fully compatible with **Ansible Collection** standards

---

## 藺 Technologies Used

| Layer         | Tool / Language       |
|---------------|------------------------|
| Orchestration | **Ansible**            |
| Language      | **Python 3** (module logic)
| OS Detection  | `platform` module      |
| Subprocesses  | `subprocess.run()`     |
| Network Check | `socket`, `ping`       |
| Packaging     | Ansible Collection structure

---

##  Where Can You Use This?

> This module is not limited to service restarts!

###  Before Restarting or Reloading Services
- Ensure **MySQL**, **Redis**, etc., are running before restarting `nginx`
- Auto-recover failed services before deploying code

### 離 Health Checks in CI/CD Pipelines
- Validate infrastructure readiness before Ansible/Terraform runs
- Gate pipeline stages based on network reachability

###  Security & Audit Automation
- Log failures of unreachable services or ports
- Run in compliance environments where dependency guarantees are required

### ☁️ Cloud Migrations or Cutovers
- Ping remote hosts or check services before redirecting traffic
- Check port availability across hybrid setups

---

##  Installation (Locally)

After building:

```bash
ansible-galaxy collection install ./sohel-dependency_checker-1.0.0.tar.gz --force
