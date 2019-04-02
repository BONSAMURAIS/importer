from rdflib.graph import Graph
from rdflib import ConjunctiveGraph, URIRef, RDFS, RDF, Literal
from SPARQLWrapper import SPARQLWrapper, POST, DIGEST, BASIC, URLENCODED
import os


def load(file_name):
    file_path = os.path.abspath(file_name)
    exists = os.path.isfile(file_path)
    print("Trying to load {}".format(file_path))
    if not exists:
        print("Error: file not found")

    if not file_path.endswith('.ttl'):
        print("Error: only ttl files supported now")


    g = Graph()
    g.parse(file_path, format="ttl")


    d_uri = URIRef('http://purl.org/dc/dcmitype/Dataset')

    results = g.triples( (None, RDF.type, d_uri) )
    s, p , o = next(results)

    query ='''
    INSERT DATA
        {{ <{}> <{}> <{}> . }}
    '''.format(s,p,o)

    print(query)

    sparql = SPARQLWrapper("https://db.bonsai.uno/bonsai/query", updateEndpoint="https://db.bonsai.uno/bonsai/update")
    sparql.setMethod(POST)
    sparql.setRequestMethod(URLENCODED)
    sparql.setHTTPAuth(BASIC)
    sparql.setCredentials("admin", "password")

    print("test2")

    sparql.setQuery(query)


    results = sparql.query()
    print(results.response.read())


