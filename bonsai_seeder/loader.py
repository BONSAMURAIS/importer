import configparser
import requests
import urllib
import sys, os

from SPARQLWrapper import SPARQLWrapper, POST, BASIC, URLENCODED, JSON, XML, TURTLE, N3
from SPARQLWrapper.SPARQLExceptions import Unauthorized
from rdflib import URIRef, BNode, RDFS, RDF, Literal
from rdflib.graph import Graph


REQUIRED_CONFIGS = ['database', 'credentials']
DATASET_TYPE_URI = URIRef('http://purl.org/dc/dcmitype/Dataset')

SPARQL_IS_DATASET_DEFINED = "ASK WHERE {{ GRAPH <{}> {{ ?s ?p ?o }} }}"
SPARQL_CREATE_DATASET = """
INSERT DATA {{
  GRAPH <{}> {{
    <{}> <{}> <{}>
  }}
}}
"""

SPARQL_DELETE_DATASET = """
DROP GRAPH <{}>
"""

SPARQL_INSERT = """
INSERT DATA {{
  GRAPH <{}> {{
    {}
  }}
}}
"""

ACTION_SKIP=1
ACTION_DELETE=2
ACTION_CONTINUE=3

METHOD_UPLOAD=1
METHOD_INSERT=2

class Loader(object):

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        for sc in REQUIRED_CONFIGS:
            if not sc in config:
                raise KeyError("Missing {} section in config file".format(sc))

        self.endpoint = config['database']['Query']
        self.update_endpoint = config['database']['Update']
        self.upload_endpoint = config['database']['Upload']

        self.endpoint_user = config['credentials']['User']
        self.endpoint_pwd =config['credentials']['Password']

        self.client = SPARQLWrapper(self.endpoint, updateEndpoint=self.update_endpoint)
        self.client.setMethod(POST)
        self.client.setRequestMethod(URLENCODED)
        self.client.setHTTPAuth(BASIC)
        self.client.setCredentials(self.endpoint_user, self.endpoint_pwd)


    def exists(self, dataset_uri):
        self.client.setQuery(SPARQL_IS_DATASET_DEFINED.format(dataset_uri))
        self.client.setReturnFormat(JSON)
        results = self.client.query()
        answer = results.convert()
        return answer['boolean']


    def update(self, query):
        self.client.setQuery(query)
        self.client.setReturnFormat(XML)
        results = self.client.query()
        message = str(results.response.read())
        return 'Success' in message, message


    def create(self, dataset_uri):
        return self.update(SPARQL_CREATE_DATASET.format(dataset_uri, dataset_uri, RDF.type, DATASET_TYPE_URI ))


    def delete(self, dataset_uri):
        return self.update(SPARQL_DELETE_DATASET.format(dataset_uri))

    def insert(self, dataset_uri, triples):
        return self.update(SPARQL_INSERT.format(dataset_uri, ". \n".join(triples) ))

    def clean(self):
        CLEAN_TRIPLES = """
        DELETE {
            ?s ?p ?o .
        } WHERE {
            ?s ?p ?o .
            FILTER NOT EXISTS { GRAPH ?g { ?s ?p ?o } }
        }
        """
        return self.update(CLEAN_TRIPLES)



    def load(self, file_name, if_exists=ACTION_SKIP, method=METHOD_UPLOAD):
        file_path = os.path.abspath(file_name)
        exists = os.path.isfile(file_path)
        print("Trying to load {}".format(file_path))

        if not exists:
            return False, "Error: {} file not found".format(file_path)

        if not file_path.endswith('.ttl'):
            return False, "Error: only ttl files supported now"

        # Load the TTL file
        g = Graph()
        g.parse(file_path, format="ttl")
        print("Parsed. Size {}".format(len(g)))
        # Check if it contains the mandatory dataset definition
        # TODO: This should be expanded to check also if author name,
        #      title, description, and licence are defined
        results = g.triples( (None, RDF.type, DATASET_TYPE_URI) )
        found = False
        dataset_uri = None

        for triple in results:
            if not found:
                found = True
                dataset_uri, _ , _ = triple
            else :
                return False, "Multiple declarations of type {} . Only one expected".format(DATASET_TYPE_URI)

        if not found:
            return False, "Missing declarations of type {} . One expected".format(DATASET_TYPE_URI)

        try:
            if not self.exists(dataset_uri):
                print("Creating graph {}".format(dataset_uri))
                success, message = self.create(dataset_uri)
                if not success:
                    return False, message
            else :
                print("Dataset {} exists".format(dataset_uri))
                if if_exists == ACTION_SKIP:
                    return True, "Skipping import"
                if if_exists == ACTION_DELETE:
                    success, message = self.delete(dataset_uri)
                    if not success:
                        return False, message

                    success, message = self.create(dataset_uri)
                    if not success:
                        return False, message

                    print("Deleted contents of {}".format(dataset_uri))

        except Unauthorized as err :
            return False, "Failed to connect to the data: access not allowed"
        except urllib.error.HTTPError as err:
            return False, "Failed to connect to the data: {}".format(err)

        success, message = True, "OK"
        if method == METHOD_UPLOAD and len(g) < 1000:
            print("Uploading contents of {}".format(file_path))
            files = { 'file': (os.path.basename(file_path), open(file_path,'rb'), 'text/turtle'), }
            response = requests.post("{}?graph={}".format(self.upload_endpoint, dataset_uri),
                                        files=files,
                                        auth=(self.endpoint_user, self.endpoint_pwd)
                                    )
            success, message = response.status_code in [200, 201], response.text
        else :
            print("Serializing iterative insertions")
            triples=[]
            for sb,pr,obj in g:
                triples.append("<{}> <{}> <{}>".format(sb, pr, obj))
                if len(triples) >= 100:
                    success, message = self.insert(dataset_uri, triples)
                    if not success:
                        return False, message
                    triples=[]
            if len(triples) > 0:
                success, message = self.insert(dataset_uri, triples)

        return success, message
