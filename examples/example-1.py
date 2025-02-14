import atsy

ats = atsy.read("data/nand.tar.gz")
print(ats.num_states)
print(ats.initial_states)
print(ats.sample_path(state=52, length=10))

ats.initial_states = [100]
atsy.write(ats, "data/nand2.tar.gz")

ats = atsy.read("data/nand2.tar.gz")
print(ats.initial_states)
