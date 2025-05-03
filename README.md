# 🔧 OpenStack Cloud Resource Automation

A simple, script-based automation tool that connects to an OpenStack cloud and allows users to:

- ✅ Create/delete volumes (e.g., 100GB data disks)
- ✅ Create private networks
- ✅ Query project resource usage (vCPUs, RAM, GPUs, volumes)


---

## 🚀 Features

- 🔐 **Secure Connection** to OpenStack using a token
- 💾 **Volume Management**: Create or delete named volumes (e.g., `dta_disk`)
- 🌐 **Network Creation**: Automatically provision private networks and subnets
- 📊 **Usage Reporting**: Return total vCPUs, RAM, GPUs, and volume GBs used

---

## 🛠️ Requirements

- Python 3.7+
- `openstacksdk`
- A valid OpenStack **API token**
- Your project and region information


