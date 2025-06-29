import os
from neo4j import GraphDatabase

EXCEL_DIR = "./data/excel/"
NEO4J_URI = "neo4j+s://0d71a2dd.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASS = "bJMtMTV6eZNNxYeRN6D4N4s5cspQLou0qTt2qjzjD40"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
