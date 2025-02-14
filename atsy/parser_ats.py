from types import SimpleNamespace

from marshmallow import Schema, ValidationError, fields, post_load, validates_schema

import atsy


class FieldUint(fields.Int):
    """Custom field for unsigned integers."""

    def _deserialize(self, value, attr, data, **kwargs):
        result = super()._deserialize(value, attr, data, **kwargs)
        if result < 0:
            raise ValidationError(f"value {value} must be an unsigned integer")
        return result


class ModelDataSchema(Schema):
    """Model data JSON schema."""

    name = fields.Str(data_key="name")
    version = fields.Str(data_key="version")
    authors = fields.List(fields.Str(), data_key="authors")
    description = fields.Str(data_key="description")
    comment = fields.Str(data_key="comment")
    doi = fields.Str(data_key="doi")
    url = fields.Str(data_key="url")

    @post_load
    def make_object(self, data, **kwargs):
        """Create an object with attributes matching the JSON fields."""
        return SimpleNamespace(**data)

    @classmethod
    def empty_object(cls):
        """Create an empty object with attributes (set to None) corresponding to the fields of JSON schema."""
        return SimpleNamespace(**{field: None for field in cls().fields})


class FileDataSchema(Schema):
    """File data JSON schema."""

    tool = fields.Str(data_key="tool")
    tool_version = fields.Str(data_key="tool-version")
    creation_date = FieldUint(data_key="creation-date")
    parameters = fields.Str(data_key="parameters")

    @post_load
    def make_object(self, data, **kwargs):
        """Create an object with attributes matching the JSON fields."""
        return SimpleNamespace(**data)

    @classmethod
    def empty_object(cls):
        """Create an empty object with attributes (set to None) corresponding to the fields of JSON schema."""
        return SimpleNamespace(**{field: None for field in cls().fields})


class AtsInfoSchema(Schema):
    """ATS index file JSON schema."""

    format_version = FieldUint(data_key="format-version", required=True)
    format_revision = FieldUint(data_key="format-revision", required=True)
    model_data = fields.Nested(ModelDataSchema, data_key="model-data")
    file_data = fields.Nested(FileDataSchema, data_key="file-data")

    # branch_values = fields.Str(data_key="branch-values", required=True)
    # branch_value_type = fields.Str(data_key="branch-value-type", required=True)

    num_players = FieldUint(data_key="#players", required=True)
    num_states = FieldUint(data_key="#states", required=True)
    # num_initial_states = FieldUint(data_key="#initial-states", required=True) # discuss
    num_choices = FieldUint(data_key="#choice", required=True)
    num_branches = FieldUint(data_key="#branches", required=True)

    @validates_schema
    def validate_fields(self, data, **kwargs):
        """ATS index file field validator."""
        pass  # will probably delegate to Ats::validate()

    @classmethod
    def empty_object(cls):
        """Create an empty object with attributes (set to None) corresponding to the fields of JSON schema."""
        obj = SimpleNamespace(**{field: None for field in cls().fields})
        obj.model_data = ModelDataSchema.empty_object()
        obj.file_data = FileDataSchema.empty_object()
        return obj

    @post_load
    def make_object(self, data, **kwargs):
        """Create an object with attributes matching the dictionary keys."""
        return SimpleNamespace(**data)


def row_start_to_ranges(row_start: list) -> list:
    """Convert row start indices to ranges."""
    ranges = []
    num_rows = len(row_start) - 1
    for row in range(num_rows):
        ranges.append(list(range(row_start[row], row_start[row + 1])))
    return ranges


def ranges_to_row_start(ranges: list) -> list:
    """Convert ranges to row start indices."""
    row_start = [interval[0] for interval in ranges]
    row_start.append(ranges[-1][-1]+1)
    assert len(row_start) == len(ranges)+1
    return row_start


def from_umb(filepath: str) -> atsy.Ats:
    """Read ATS from a tarbal file."""
    filename_data = atsy.tar_read(filepath)
    ats = atsy.Ats()
    index = AtsInfoSchema().load(atsy.json_from_bytes(filename_data["index.json"]))

    ats.index = index
    ats.num_players = index.num_players
    ats.num_states = index.num_states
    ats.num_choices = index.num_choices
    ats.num_branches = index.num_branches

    ats.initial_states = atsy.vector_from_bytes(filename_data["initial-states.bin"], "uint")
    ats.state_choices = row_start_to_ranges(atsy.vector_from_bytes(filename_data["state-to-choice.bin"], "uint"))
    ats.choice_branches = row_start_to_ranges(atsy.vector_from_bytes(filename_data["choice-to-branch.bin"], "uint"))
    ats.branch_target = atsy.vector_from_bytes(filename_data["branch-to-target.bin"], "uint")

    if "branch-to-value.bin" in filename_data:
        ats.branch_value = atsy.vector_from_bytes(filename_data["branch-to-value.bin"], "double")

    ats.validate()
    return ats


def to_umb(ats: atsy.Ats, filepath: str):
    """Store ATS to a tarball file."""
    ats.validate()

    ats.index.num_players = ats.num_players
    ats.index.num_states = ats.num_states
    ats.index.num_choices = ats.num_choices
    ats.index.num_branches = ats.num_branches

    filename_data = {}
    filename_data["index.json"] = atsy.json_to_bytes(AtsInfoSchema().dump(ats.index))
    filename_data["initial-states.bin"] = atsy.vector_to_bytes(ats.initial_states, "uint")
    filename_data["state-to-choice.bin"] = atsy.vector_to_bytes(ranges_to_row_start(ats.state_choices), "uint")
    filename_data["choice-to-branch.bin"] = atsy.vector_to_bytes(ranges_to_row_start(ats.choice_branches), "uint")
    filename_data["branch-to-target.bin"] = atsy.vector_to_bytes(ats.branch_target, "uint")
    if ats.branch_value is not None:
        filename_data["branch-to-value.bin"] = atsy.vector_to_bytes(ats.branch_value, "double")
    atsy.tar_write(filepath, filename_data)
