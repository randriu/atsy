import io
import json
import os
import struct
import tarfile


def type_str_to_struct_format(value_type: str) -> str:
    table = {
        "uint": "Q",
        "double": "d",
    }
    if value_type not in table:
        raise ValueError(f"value type must be in {table} but is {value_type}")
    return table[value_type]


def type_to_size(value_type: str) -> int:
    table = {
        "uint": 8,
        "double": 8,
    }
    if value_type not in table:
        raise ValueError(f"value type must be in {table} but is {value_type}")
    return table[value_type]


def endianness_to_struct_format(little_endian: bool):
    """
    endianness: True for little-endian, False for big-endian
    """
    table = {False: ">", True: "<"}
    if little_endian not in table:
        raise ValueError(f"endianness must be in {table} but is {little_endian}")
    return table[little_endian]


def vector_from_bytes(vector_bytes: bytes, value_type: str, little_endian: bool = True) -> list:
    """
    Decode a binary string as a list of numbers.

    :param value_type: vector element type, must be in {"uint", "double"}
    """
    value_size = type_to_size(value_type)
    type_format = type_str_to_struct_format(value_type)
    order_format = endianness_to_struct_format(little_endian)
    num_count = len(vector_bytes) // value_size
    vector = struct.unpack(f"{order_format}{num_count}{type_format}", vector_bytes)
    return list(vector)


def vector_to_bytes(vector: list, value_type: str, little_endian: bool = True) -> bytes:
    """Encode as list of number as a binary string."""
    type_format = type_str_to_struct_format(value_type)
    assert len(vector) > 0
    for item in vector:
        assert isinstance(item, int) or isinstance(item, float)
        if value_type == "uint":
            assert isinstance(item, int) and item >= 0
    order_format = endianness_to_struct_format(little_endian)
    return struct.pack(f"{order_format}{len(vector)}{type_format}", *vector)


def remove_none(json_obj: dict | list):
    """Recursively remove all None (null) values from the JSON object."""
    if isinstance(json_obj, dict):
        return {k: remove_none(v) for k, v in json_obj.items() if v is not None}
    elif isinstance(json_obj, list):
        return [remove_none(v) for v in json_obj]
    else:
        return json_obj


def json_from_bytes(json_bytes: bytes) -> dict | list:
    """Decode a binary string as a JSON dict/list."""
    return json.loads(json_bytes.decode("utf-8"))


def json_to_bytes(json_obj: dict | list, indent: int = 4) -> bytes:
    """Encode a JSON object as a binary string."""
    return json.dumps(remove_none(json_obj), indent=indent).encode("utf-8")


def tar_read(tarpath: str) -> dict:
    """
    Read contents of a tarball file.

    :param tarpath: path to a tarball file; may end with .gz to indicate that the file is gzipped
    :returns: a dictionary of filename - binary string pairs
    """
    # use file extension to see whether the tar was zipped
    filename_data = {}
    mode = "r"
    if tarpath.endswith(".gz"):
        mode = "r:gz"
    with tarfile.open(tarpath, mode=mode) as tar:
        for member in tar.getmembers():
            if member.isfile():
                filename_data[member.name] = tar.extractfile(member).read()
    return filename_data


def tar_write(tarpath: str, filename_data: dict):
    """
    Create a tarball file with the given contents.

    :param tarpath: path to a tarball file; may end with .gz to indicate that the file is gzipped
    :param filename_data: a dictionary of filename - binary string pairs
    """
    mode = "w"
    if tarpath.endswith(".gz"):
        mode = "w:gz"
    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode=mode) as tar:
        for filename, data in filename_data.items():
            tar_info = tarfile.TarInfo(name=filename)
            tar_info.size = len(data)
            tar.addfile(tar_info, io.BytesIO(data))
    tar_bytes = tar_stream.getvalue()
    with open(tarpath, "wb") as file:
        file.write(tar_bytes)
    print(f"data exported to {tarpath}")
