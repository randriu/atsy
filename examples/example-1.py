import atsy

ats = atsy.from_umb("data/consensus-2-2.tar.gz")
print(ats.num_states)
print(ats.initial_states)
print(ats.sample_path(state=52, length=10))

ats.initial_states = [100]
atsy.to_umb(ats, "data/alt.tar.gz")

ats = atsy.from_umb("data/alt.tar.gz")
print(ats.initial_states)
