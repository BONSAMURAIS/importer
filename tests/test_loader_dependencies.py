from unittest.mock import Mock

import pytest
from rdflib import Graph, Literal, URIRef

from bonsai_seeder.loader import Loader, METHOD_INSERT


@pytest.fixture
def loader(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.ini").write_text(
        "[database]\nQuery = http://localhost/query\n"
        "Update = http://localhost/update\nUpload = http://localhost/upload\n"
        "[credentials]\nUser = user\nPassword = password\n"
    )
    instance = Loader()
    instance.exists = Mock(return_value=False)
    instance.create = Mock(return_value=(True, "Success"))
    return instance


@pytest.fixture
def dataset(tmp_path):
    path = tmp_path / "dataset.ttl"
    path.write_text(
        '@prefix dcmitype: <http://purl.org/dc/dcmitype/> .\n'
        '<http://example.org/dataset> a dcmitype:Dataset ;\n'
        '    <http://example.org/title> "Example"@en .\n'
    )
    return path


def test_upload_uses_parsed_dataset(loader, dataset, monkeypatch):
    post = Mock(return_value=Mock(status_code=201, text="Created"))
    monkeypatch.setattr("bonsai_seeder.loader.requests.post", post)

    assert loader.load(str(dataset)) == (True, "Created")
    loader.create.assert_called_once_with(URIRef("http://example.org/dataset"))
    assert post.call_args.args[0] == "http://localhost/upload?graph=http://example.org/dataset"
    assert post.call_args.kwargs["auth"] == ("user", "password")
    post.call_args.kwargs["files"]["file"][1].close()


def test_insert_serializes_literals(loader, dataset, monkeypatch):
    loader.insert = Mock(return_value=(True, "Success"))
    monkeypatch.setattr("bonsai_seeder.loader.sleep", lambda _: None)

    assert loader.load(str(dataset), method=METHOD_INSERT) == (True, "Success")
    triples = loader.insert.call_args.args[1]
    graph = Graph().parse(data=" .\n".join(triples) + " .", format="nt")
    assert (URIRef("http://example.org/dataset"),
            URIRef("http://example.org/title"), Literal("Example", lang="en")) in graph
