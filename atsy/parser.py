import os
import struct


def type_to_struct_format(value_type):
    table = {int: "Q", float: "d"}
    if value_type not in table:
        raise ValueError(f"value type must be in {table} but is {value_type}")
    return table[value_type]


def endianness_to_struct_format(endianness):
    """
    endianness: True for big-endian, False for little-endian
    """
    table = {True: ">", False: "<"}
    if endianness not in table:
        raise ValueError(f"endianness must be in {table} but is {endianness}")
    return table[endianness]


def vector_export(filename, vector, big_endian=True):
    """
    Exports a list of numbers to a binary file.
    """
    assert len(vector) > 0
    value_type = type_to_struct_format(type(vector[0]))
    byte_order = endianness_to_struct_format(big_endian)

    with open(filename, "wb") as f:
        f.write(struct.pack(f"{byte_order}{len(vector)}{value_type}", *vector))


def vector_import(filename, dtype=int, big_endian=True):
    """
    Imports a list of numbers from a binary file.

    :param filename: name of the input file
    :param dtype: input number value type (int,float)
    :returns: vector
    :raises ValueError: when?
    """
    type_size = 8  # both 'd' (double) and 'Q' (unsigned 8-byte int) are 8 bytes each
    byte_order = endianness_to_struct_format(big_endian)
    value_type = type_to_struct_format(dtype)
    with open(filename, "rb") as f:
        num_count = os.path.getsize(filename) // type_size
        vector = struct.unpack(f"{byte_order}{num_count}{value_type}", f.read())
    return list(vector)
