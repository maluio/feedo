# diagram.py
from diagrams import Diagram, Edge, Cluster
from diagrams.programming.framework import Django
from diagrams.onprem.container import Docker
from diagrams.aws.storage import S3
from diagrams.onprem.network import Traefik
from diagrams.generic.database import SQL

# https://diagrams.mingrammer.com/docs/getting-started/installation
with Diagram("Feedo - Recommended Architecture", filename="docs/feedo-architecture"):
    with Cluster("On Prem"):
        web = Traefik()
        docker = Docker()

        with Cluster("App"):
            app = Django()
            db = SQL("SQLite")
    with Cluster("AWS"):
        litestream = Edge(label="litestream")
        s3 = S3("S3 DB backup")

    web >> docker >> app >> db >> litestream >> s3
