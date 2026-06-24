from neo4j import GraphDatabase
from datetime import datetime

NEO4J_URI = "bolt://localhost:7688"
NEO4J_USER = "neo4j"
NEO4J_PASS = "password123"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


# -------------------------
# SCAN NODE
# -------------------------

def create_scan(domain):
    with driver.session() as session:
        result = session.run("""
        CREATE (s:Scan {
            id: randomUUID(),
            domain: $domain,
            timestamp: $time
        })
        RETURN s.id AS id
        """, domain=domain, time=str(datetime.now()))
        return result.single()["id"]


# -------------------------
# DOMAIN
# -------------------------

def create_domain(scan_id, domain):
    with driver.session() as session:
        session.run("""
        MATCH (s:Scan {id:$scan_id})
        MERGE (d:Domain {name:$domain})
        MERGE (s)-[:ON_DOMAIN]->(d)
        """, scan_id=scan_id, domain=domain)


# -------------------------
# SUBDOMAINS
# -------------------------

def add_subdomains(scan_id, domain, subs):
    with driver.session() as session:
        for sub in subs:
            session.run("""
            MATCH (s:Scan {id:$scan_id})
            MATCH (d:Domain {name:$domain})
            MERGE (sd:Subdomain {name:$sub})
            MERGE (d)-[:HAS_SUBDOMAIN]->(sd)
            MERGE (s)-[:DISCOVERED]->(sd)
            """, scan_id=scan_id, domain=domain, sub=sub)


# -------------------------
# ALIVE HOSTS
# -------------------------

def add_alive(scan_id, hosts):
    with driver.session() as session:
        for h in hosts:
            session.run("""
            MATCH (s:Scan {id:$scan_id})
            MERGE (h:HTTPService {url:$host})
            MERGE (s)-[:DISCOVERED]->(h)
            """, scan_id=scan_id, host=h)


