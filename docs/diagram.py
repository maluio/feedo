# diagram.py
from diagrams import Diagram, Edge, Cluster
from diagrams.programming.framework import Django
from diagrams.aws.storage import S3
from diagrams.onprem.network import Traefik, Gunicorn, Caddy
from diagrams.generic.database import SQL
from diagrams.onprem.client import User

# https://www.graphviz.org/doc/info/attrs.html
graph_attr = {
    "pad": "0.5",
}

# https://diagrams.mingrammer.com/docs/getting-started/installation
with Diagram("Feedo - Recommended Architecture", filename="docs/feedo-architecture", graph_attr=graph_attr):
    with Cluster("Public Internet"):
        user = User("User")

    with Cluster("On Prem"):
        with Cluster("Routing + Access Control"):
            web = Traefik("HTTP Basic Auth")

        with Cluster("Container"):
            with Cluster("WSGI Server"):
                app_server = Gunicorn("Gunicorn")
            with Cluster("Feedo"):
                app = Django()
                db = SQL("SQLite")
    with Cluster("AWS"):
        litestream = Edge(label="litestream")
        s3 = S3("S3 DB backup")

    user >> web >> app_server >> app >> db >> litestream >> s3


with Diagram("Feedo - Simple Architecture", filename="docs/feedo-architecture-simple", graph_attr=graph_attr):
    with Cluster("Public Internet"):
        user = User("User")

    with Cluster("On Prem"):
        with Cluster("Routing + Access Control"):
            web = Caddy("HTTP Basic Auth")

        with Cluster("Feedo"):
            app = Django("./manage.py runserver")
            db = SQL("SQLite")

    user >> web >> app >> db
