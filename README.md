# Install Frappe with PostgreSQL and Multitenancy (Shared Database)

This script simplifies the installation of Frappe using PostgreSQL as the database backend and sets up multitenancy with a shared database.

---

## How to Use

### Step 1: Download the Installation Script

Download the script to your environment using `wget`:

```bash
wget https://raw.githubusercontent.com/Amein-Eskinder/frappe/main/easy-install.py
```

---

### Step 2: Run the Script Based on Your Environment

You can choose between a **production** or **development** setup based on your needs.

#### For Production Setup:
Run the following command to install Frappe in a production-ready environment:

```bash
python3 easy-install.py --prod
```

#### For Development Setup:
Run the following command to install Frappe for development purposes:

```bash
python3 easy-install.py --dev
```

---

### Step 3: Access Frappe

Once the installation is complete, access your Frappe site in a web browser.

- For **Production Environment**:  
  `http://<your_server_ip>:8000`

- For **Development Environment**:  
  `http://localhost:8000`

---

## Features

- **PostgreSQL Database**: Robust and scalable database management.
- **Multitenancy**: Supports multiple sites with a shared database.
- **Environment Flexibility**: Choose between production and development setups.
- **Docker Support**: Fully containerized for ease of deployment.

---

## Multitenancy Usage

After installation, you can manage multiple sites using these Frappe commands:

1. **Create a New Site**:
   ```bash
   bench new-site <sitename> --db-type postgres
   ```

2. **Switch Between Sites**:
   ```bash
   bench use <sitename>
   ```

3. **List Existing Sites**:
   ```bash
   bench list-sites
   ```

---

## Requirements

- Python 3.8 or later
- Docker and Docker Compose installed
- Internet connection
- Minimum 2GB RAM (4GB recommended)

---

## Troubleshooting

- **Docker Issues**: Ensure Docker and Docker Compose are properly installed and running.
- **Access Problems**: Verify that ports 8000 (Frappe) and 5432 (PostgreSQL) are open.
- **Dependency Errors**: Ensure system dependencies are installed before running the script.

---

This script streamlines the setup process, allowing you to quickly deploy Frappe with PostgreSQL and multitenancy.

Contributions and feedback are welcome!

---

