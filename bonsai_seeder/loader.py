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

IS_DATASET_DEFINED = "ASK WHERE {{ GRAPH <{}> {{ ?s ?p ?o }} }}"
CREATE_DATASET = """
INSERT DATA {{
  GRAPH <{}> {{
    <{}> <{}> <{}>
  }}
}}
"""

DELETE_DATASET = """
DROP GRAPH <{}>
"""

INSERT = """
INSERT DATA {{
  GRAPH <{}> {{
    {}
  }}
}}
"""



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
        self.client.setQuery(IS_DATASET_DEFINED.format(dataset_uri))
        self.client.setReturnFormat(JSON)
        results = self.client.query()
        answer = results.convert()
        return answer['boolean']

    def update(self, query):
        self.client.setQuery(query)
        self.client.setReturnFormat(XML)
        results = self.client.query()
        return 'Success' in str(results.response.read())


    def create(self, dataset_uri):
        return self.update(CREATE_DATASET.format(dataset_uri, dataset_uri, RDF.type, DATASET_TYPE_URI ))

    def delete(self, dataset_uri):
        return self.update(DELETE_DATASET.format(dataset_uri))



    def load(self, file_name):
        file_path = os.path.abspath(file_name)
        exists = os.path.isfile(file_path)
        #print("Trying to load {}".format(file_path))

        if not exists:
            print("Error: {} file not found".format(file_path), file=sys.stderr)
            return False

        if not file_path.endswith('.ttl'):
            print("Error: only ttl files supported now", file=sys.stderr)
            return False

        # Load the TTL file
        g = Graph()
        g.parse(file_path, format="ttl")

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
                print("Multiple declarations of type {} . Only one expected".format(DATASET_TYPE_URI), file=sys.stderr)
                return False

        try:
            if not self.exists(dataset_uri):
                print("Creating graph {}".format(dataset_uri))
                self.create(dataset_uri)
            else :
                print("Dataset exists")
                # self.delete(dataset_uri)
                # print("deleted {}".format(dataset_uri))
                # return False
        except Unauthorized as err :
            print("Failed to connect to the data: access not allowed", file=sys.stderr)
            return False
        except urllib.error.HTTPError as err:
            print("Failed to connect to the data", file=sys.stderr)
            print(err, file=sys.stderr)
            return False

        print("Uploading contents of {}".format(file_path))
        files = { 'file': (os.path.basename(file_path), open(file_path,'rb'), 'text/turtle'), }
        response = requests.post("{}?graph={}".format(self.upload_endpoint, dataset_uri),
                                    files=files,
                                    auth=(self.endpoint_user, self.endpoint_pwd)
                                )
        print("Response:")
        print(response.text)

        return response.status_code in [200, 201]
