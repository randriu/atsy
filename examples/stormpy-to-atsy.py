import argparse
import stormpy

import atsy
from pathlib import Path

def existing_prism_file(path):
    """Check if the file exists and has a .prism extension."""
    p = Path(path)
    if not p.is_file():
        raise argparse.ArgumentTypeError(f"File '{path}' does not exist.")
    if p.suffix != ".prism":
        raise argparse.ArgumentTypeError(f"File '{path}' is not a .prism file.")
    return p

parser = argparse.ArgumentParser()
parser.add_argument("input_path", type=existing_prism_file, help="path to a PRISM model")
args = parser.parse_args()
input_path = args.input_path

model_name = input_path.stem
print(model_name)
prism_path = str(input_path)
drn_path = str(input_path.with_suffix(".drn"))
tar_path = str(input_path.with_suffix(".tar.gz"))

print(f"building {prism_path}...")
prism = stormpy.parse_prism_program(prism_path)
model = stormpy.build_model(prism)
stormpy.export_to_drn(model, drn_path)

print(f"building {tar_path}...")
ats = atsy.Ats()

# TODO
ats.index.format_version = 1
ats.index.format_revision = 0


ats.index.model_data.name = model_name
ats.index.file_data.tool = "atsy"
ats.index.file_data.tool_version = atsy.__version__

ats.num_players = 1
ats.num_states = model.nr_states
ats.num_choices = model.nr_choices
ats.num_branches = 0

ats.initial_states = list(model.initial_states)

ats.state_choices = [ None ] * ats.num_states
ats.choice_branches = [ None ] * ats.num_choices
ats.branch_target = []
ats.branch_value = []

tm = model.transition_matrix
for state in range(ats.num_states):
    ats.state_choices[state] = list(range(tm.get_row_group_start(state),tm.get_row_group_end(state)))
    for choice in ats.state_choices[state]:
        branch_start = ats.num_branches
        for entry in tm.get_row(choice):
            ats.branch_target.append(entry.column)
            ats.branch_value.append(entry.value())
            ats.num_branches += 1
        branch_end = ats.num_branches
        assert branch_start < branch_end
        ats.choice_branches[choice] =  list(range(branch_start, branch_end))

atsy.to_umb(ats, tar_path)
