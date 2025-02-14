import stormpy

import atsy

model_name = "consensus-6-2"
prism_filename = f"{model_name}.prism"
drn_filename = f"{model_name}.drn"
tar_filename = f"{model_name}.tar.gz"
print(f"building {prism_filename}...")
prism = stormpy.parse_prism_program(prism_filename)
model = stormpy.build_model(prism)
stormpy.export_to_drn(model, drn_filename)

print(f"building {tar_filename}...")
ats = atsy.Ats()
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

ats.state_choices = [ None ] * ats.num_states
ats.choice_branches = [ None ] * ats.num_choices
ats.branch_to_target = []
ats.branch_to_value = []

tm = model.transition_matrix
for state in range(ats.num_states):
    ats.state_choices[state] = list(range(tm.get_row_group_start(state),tm.get_row_group_end(state)))
    for choice in ats.state_choices[state]:
        branch_start = ats.num_branches
        for entry in tm.get_row(choice):
            ats.branch_to_target.append(entry.column)
            ats.branch_to_value.append(entry.value())
            ats.num_branches += 1
        branch_end = ats.num_branches
        ats.choice_branches[choice] =  list(range(branch_start, branch_end))

atsy.write(ats, tar_filename)
