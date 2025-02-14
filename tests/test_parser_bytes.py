import importlib.resources
import tempfile

import pytest

import atsy


@pytest.mark.parametrize(
    "vector, value_type",
    [
        ([3.14, 0, 150.5, -1 / 7], "double"),
        ([0, 2, 76, 5], "uint"),
    ],
)
def test_vector_bytes(vector, value_type):
    vector_in = vector
    vector_bytes = atsy.vector_to_bytes(vector_in, value_type)
    assert isinstance(vector_bytes, bytes)
    vector_out = atsy.vector_from_bytes(vector_bytes, value_type)
    assert len(vector_in) == len(vector_out)
    for i in range(len(vector_in)):
        assert vector_in[i] == vector_out[i]


def test_json_bytes():
    json_in = {"a": 0, "b": "c", "c": {"aa": ["alex", "bob"]}, "d": None}
    json_bytes = atsy.json_to_bytes(json_in)
    assert isinstance(json_bytes, bytes)
    json_out = atsy.json_from_bytes(json_bytes)
    assert json_in["a"] == json_out["a"]
    assert "d" not in json_out


def test_tar():
    filename_data = atsy.tar_read("data/nand.tar.gz")
    assert "index.json" in filename_data
    for data in filename_data.values():
        assert isinstance(data, bytes)
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        atsy.tar_write(temp_file.name, filename_data)
