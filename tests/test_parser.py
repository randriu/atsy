import tempfile

import atsy


def test_vector_export_double():
    return
    vector = [3.14, 2.71, 1.41, 1.73]
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        atsy.vector_export(temp_file.name, vector)


def test_vector_export_unsigned_integer():
    vector = [5, 42, 0, 100]
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        atsy.vector_export(temp_file.name, vector)


def test_vector_import():
    vector = atsy.vector_import("data/vector-double.bin", dtype=float)
    assert vector[0] == 3.14

    vector = atsy.vector_import("data/vector-uint.bin", dtype=int)
    assert vector[0] == 5
