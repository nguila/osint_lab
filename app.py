from flask import Flask, request, render_template_string
from neo4j import GraphDatabase

app = Flask(__name__)

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password123")
)


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>OSINT Graph</title>
    <style>
        body { font-family: Arial; background:#0b1220; color:white; }
        input { padding:10px; width:300px; }
        .box { margin:20px; }
        pre { background:#111827; padding:10px; }
    </style>
</head>
<body>

<h1>OSINT Graph Search</h1>

<form method="GET">
    <input name="q" placeholder="domain / subdomain / ip">
    <button>Search</button>
</form>

<div class="box">
<pre>{{data}}</pre>
</div>

</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    q = request.args.get("q")

    data = []

    if q:
        with driver.session() as session:
            result = session.run("""
            MATCH (n)
            WHERE n.name CONTAINS $q OR n.address CONTAINS $q
            RETURN n LIMIT 50
            """, q=q)

            for r in result:
                data.append(dict(r["n"]))

    return render_template_string(HTML, data=data)


if __name__ == "__main__":
    app.run(debug=True)


