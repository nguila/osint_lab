import sys
import subprocess
import json
import os
from datetime import datetime

from neo4j_engine import (
    create_scan,
    create_domain,
    add_subdomains,
    add_alive
)


def run(cmd):
    print(f"[CMD] {cmd}")
    return subprocess.getoutput(cmd)


def subfinder(domain):
    output = run(f"subfinder -d {domain} -silent")

    results = [
        line.strip()
        for line in output.splitlines()
        if line.strip()
    ]

    return list(set(results))


def amass(domain):
    cmd = (
        "docker compose -f ~/amass/compose.yaml "
        f"exec -T engine amass enum -d {domain}"
    )

    output = run(cmd)

    results = []

    for line in output.splitlines():
        line = line.strip()

        if line and domain in line:
            results.append(line)

    return list(set(results))


def httpx(domains):
    if not domains:
        return []

    hosts_file = "/tmp/hosts.txt"

    with open(hosts_file, "w") as f:
        f.write("\n".join(domains))

    output = run(f"httpx -l {hosts_file} -silent")

    results = [
        line.strip()
        for line in output.splitlines()
        if line.strip()
    ]

    return list(set(results))


def ingest(domain):

    print(f"\n[+] OSINT ENGINE START: {domain}\n")

    data = {
        "domain": domain,
        "timestamp": str(datetime.now()),
        "subdomains": [],
        "amass": [],
        "alive_hosts": []
    }

    print("\n[1] Subfinder")
    subs = subfinder(domain)

    print("\n[2] Amass")
    amass_result = amass(domain)

    all_domains = list(set(subs + amass_result))

    print("\n[3] HTTPX")
    alive = httpx(all_domains)

    data["subdomains"] = subs
    data["amass"] = amass_result
    data["alive_hosts"] = alive

    print("\n[4] Neo4j ingest")

    try:
        scan_id = create_scan(domain)

        create_domain(
            scan_id,
            domain
        )

        add_subdomains(
            scan_id,
            domain,
            all_domains
        )

        add_alive(
            scan_id,
            alive
        )

    except Exception as e:
        print(f"[!] Neo4j error: {e}")

    print("\n[+] Pipeline concluído")

    return data


def save(data):

    output_dir = "results"

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    file_path = os.path.join(
        output_dir,
        "osint_result.json"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"\n[+] Guardado em {file_path}")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Uso: python3 osint_engine.py dominio.com")
        sys.exit(1)

    domain = sys.argv[1]

    result = ingest(domain)

    save(result)

