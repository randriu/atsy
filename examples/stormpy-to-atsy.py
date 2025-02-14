import stormpy

import atsy

path = "nand.v1.prism"
prism = stormpy.parse_prism_program(path)
model = stormpy.build_model(prism)

stormpy.export_to_drn(model, "model.drn")
ats = atsy.Ats()

tm = model.transition_matrix

ats.index.creation_info.tool = "atsy"
ats.index.creation_info.version = atsy.__version__

# TODO
ats.index.format_version = 1
ats.index.format_revision = 0

ats.num_players = 1
ats.num_states = model.nr_states
ats.num_choices = model.nr_choices
ats.num_branches = 0

ats.initial_states = list(model.initial_states)

ats.choice_branches = []

ats.branch_to_target = []
ats.branch_to_value = []

# if model.model_type ==
if model.model_type == stormpy.storage.ModelType.DTMC:
    ndi = list(range(ats.num_states + 1))
    ats.state_choices = atsy.row_start_to_ranges(ndi)
else:
    print("yo")
    exit()
for choice in range(ats.num_choices):
    branch_start = ats.num_branches
    for entry in tm.get_row(choice):
        ats.branch_to_target.append(entry.column)
        ats.branch_to_value.append(entry.value())
        ats.num_branches += 1
    branch_end = ats.num_branches
    ats.choice_branches.append(list(range(branch_start, branch_end)))

atsy.write(ats, "nand.tar.gz")
exit()
