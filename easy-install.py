#!/usr/bin/env python3

import argparse
import logging
import os
import platform
import subprocess
import sys
import time
import urllib.request
from shutil import move, unpack_archive, which
from typing import Dict

logging.basicConfig(
    filename="easy-install.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Default configurations
PROD_CONFIG = {
    "site": "taywan.cloud",
    "project": "taywan",  # Changed to lowercase
    "email": "Amein@taywan.cloud"
}

DEV_CONFIG = {
    "site": "dev.taywan.cloud",
    "project": "taywan-dev",  # Changed to lowercase with hyphen
    "email": "Amein@taywan.cloud"
}

def cprint(*args, level: int = 1):
    """
    logs colorful messages
    level = 1 : RED
    level = 2 : GREEN
    level = 3 : YELLOW
    """
    CRED = "\033[31m"
    CGRN = "\33[92m"
    CYLW = "\33[93m"
    reset = "\033[0m"
    message = " ".join(map(str, args))
    if level == 1:
        print(CRED, message, reset)
    if level == 2:
        print(CGRN, message, reset)
    if level == 3:
        print(CYLW, message, reset)

def generate_pass(length: int = 12) -> str:
    import math
    import secrets
    if not length:
        length = 56
    return secrets.token_hex(math.ceil(length / 2))[:length]

def clone_frappe_docker_repo() -> None:
    try:
        urllib.request.urlretrieve(
            "https://github.com/frappe/frappe_docker/archive/refs/heads/main.zip",
            "frappe_docker.zip",
        )
        unpack_archive("frappe_docker.zip", ".")
        move("frappe_docker-main", "frappe_docker")
        os.remove("frappe_docker.zip")
        logging.info("Frappe Docker repo cloned successfully")
    except Exception as e:
        logging.error("Clone failed", exc_info=True)
        cprint("Cloning failed:", str(e), level=1)
        sys.exit(1)

def write_to_env(wd: str, config: Dict) -> None:
    """Write environment configuration for Postgres and multi-tenancy"""
    db_pass = generate_pass(16)
    admin_pass = generate_pass(16)
    
    with open(os.path.join(wd, ".env"), "w") as f:
        f.writelines([
            f"FRAPPE_VERSION=v15\n",
            f"DB_TYPE=postgres\n",
            f"DB_HOST=postgres\n",
            f"DB_PORT=5432\n",
            f"DB_NAME=postgres\n",
            f"DB_PASSWORD={db_pass}\n",
            f"DB_USER=postgres\n",
            f"REDIS_CACHE=redis-cache:6379\n",
            f"REDIS_QUEUE=redis-queue:6379\n",
            f"REDIS_SOCKETIO=redis-socketio:6379\n",
            f"REDIS_PASSWORD={generate_pass(16)}\n",
            f"SITE_NAME={config['site']}\n",
            f"SITES={config['site']}\n",
            f"ADMIN_PASSWORD={admin_pass}\n",
            f"LETSENCRYPT_EMAIL={config['email']}\n",
            f"USE_SHARED_DB=1\n"
        ])
    
    # Save passwords
    with open(os.path.join(os.path.expanduser("~"), "frappe_passwords.txt"), "w") as f:
        f.writelines([
            f"Site: {config['site']}\n",
            f"Admin Password: {admin_pass}\n",
            f"DB Password: {db_pass}\n"
        ])

def setup_instance(is_prod: bool = True):
    """Setup Frappe instance"""
    config = PROD_CONFIG if is_prod else DEV_CONFIG
    
    if not os.path.exists("frappe_docker"):
        clone_frappe_docker_repo()
    
    docker_repo_path = os.path.join(os.getcwd(), "frappe_docker")
    write_to_env(docker_repo_path, config)
    
    compose_file = os.path.join(os.path.expanduser("~"), f"{config['project']}-compose.yml")
    
    try:
        # Generate compose file
        with open(compose_file, "w") as f:
            subprocess.run([
                "docker", "compose",
                "--project-name", config['project'],
                "-f", "compose.yaml",
                "-f", "overrides/compose.postgres.yaml",
                "-f", "overrides/compose.redis.yaml",
                "-f", "overrides/compose.https.yaml",
                "--env-file", ".env",
                "config"
            ], cwd=docker_repo_path, stdout=f, check=True)
        
        # Deploy
        subprocess.run([
            "docker", "compose",
            "-p", config['project'],
            "-f", compose_file,
            "up", "-d"
        ], check=True)
        
        cprint(f"\nDeployment successful! Access your site at https://{config['site']}\n", level=2)
        cprint("Credentials saved in ~/frappe_passwords.txt", level=3)
        
    except Exception as e:
        logging.error("Setup failed", exc_info=True)
        cprint("Setup failed:", str(e), level=1)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install Frappe with Docker")
    parser.add_argument("-p", "--prod", help="Setup Production System", action="store_true")
    parser.add_argument("-d", "--dev", help="Setup Development System", action="store_true")
    
    args = parser.parse_args()
    
    if args.prod:
        cprint("\nSetting up Production Instance\n", level=2)
        setup_instance(is_prod=True)
    elif args.dev:
        cprint("\nSetting up Development Instance\n", level=2)
        setup_instance(is_prod=False)
    else:
        parser.print_help()