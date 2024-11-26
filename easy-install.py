#!/usr/bin/env python3

import argparse
import logging
import os
import subprocess
import sys
from shutil import move, unpack_archive
from typing import Dict
import urllib.request

logging.basicConfig(
    filename="easy-install.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Default configurations
PROD_CONFIG = {
    "site": "taywan.cloud",
    "project": "taywan",
    "email": "Amein@taywan.cloud"
}

DEV_CONFIG = {
    "site": "dev.taywan.cloud",
    "project": "taywan-dev",
    "email": "Amein@taywan.cloud"
}

def cprint(*args, level: int = 1):
    CRED = "\033[31m"
    CGRN = "\33[92m"
    CYLW = "\33[93m"
    reset = "\033[0m"
    message = " ".join(map(str, args))
    print(f"{[CRED, CGRN, CYLW][level-1]}{message}{reset}")

def generate_pass(length: int = 12) -> str:
    import secrets
    return secrets.token_hex(length)

def clone_frappe_docker_repo() -> None:
    try:
        if os.path.exists("frappe_docker"):
            cprint("Docker repo already exists", level=3)
            return
            
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

def write_env_file(config: Dict) -> None:
    db_pass = generate_pass()
    redis_pass = generate_pass()
    admin_pass = generate_pass()
    
    env_content = f"""FRAPPE_VERSION=v15
DB_HOST=postgres
DB_PORT=5432
DB_NAME=postgres
DB_PASSWORD={db_pass}
DB_USER=postgres
DB_TYPE=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_PASSWORD={db_pass}
POSTGRES_USER=postgres
POSTGRES_DB=postgres
REDIS_CACHE=redis-cache:6379
REDIS_QUEUE=redis-queue:6379
REDIS_SOCKETIO=redis-socketio:6379
REDIS_PASSWORD={redis_pass}
SITE_NAME={config['site']}
SITES='{config['site']}'
ADMIN_PASSWORD={admin_pass}
LETSENCRYPT_EMAIL={config['email']}
USE_SHARED_DB=1
"""
    
    with open("frappe_docker/.env", "w") as f:
        f.write(env_content)
        
    # Save credentials
    with open(os.path.expanduser("~/frappe_passwords.txt"), "w") as f:
        f.write(f"""Site: {config['site']}
Admin Password: {admin_pass}
DB Password: {db_pass}
Redis Password: {redis_pass}
""")

def setup_instance(is_prod: bool = True):
    config = PROD_CONFIG if is_prod else DEV_CONFIG
    clone_frappe_docker_repo()
    write_env_file(config)
    
    try:
        compose_commands = [
            "docker", "compose",
            "--project-name", config['project'],
            "-f", "compose.yaml",
            "-f", "overrides/compose.postgres.yaml",
            "-f", "overrides/compose.redis.yaml"
        ]
        
        if is_prod:
            compose_commands.extend(["-f", "overrides/compose.https.yaml"])
            
        compose_commands.extend(["--env-file", ".env", "up", "-d"])
        
        subprocess.run(compose_commands, cwd="frappe_docker", check=True)
        
        cprint(f"\nDeployment successful!", level=2)
        cprint(f"Access your site at: {'https' if is_prod else 'http'}://{config['site']}", level=2)
        cprint("Credentials saved in ~/frappe_passwords.txt", level=3)
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Docker command failed: {e.stderr}", exc_info=True)
        cprint(f"Setup failed: {e}", level=1)
        sys.exit(1)
    except Exception as e:
        logging.error("Setup failed", exc_info=True)
        cprint(f"Setup failed: {e}", level=1)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install Frappe with PostgreSQL")
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