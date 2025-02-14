import collections
import random

import atsy


class Ats:
    """Annotated transition system."""

    def __init__(self):
        self.index = atsy.AtsInfoSchema.default_object()

        self.num_players = None
        self.num_states = None
        self.num_choices = None
        self.num_branches = None

        self.initial_states = None
        self.state_choices = None
        self.choice_branches = None
        self.branch_to_target = None
        self.branch_to_value = None
        self.annotations = None

    def validate(self):

        def assert_is_list(l, name, length=None):
            if not isinstance(l,list):
                raise ValueError(f"{name} must be a list")
            if length is not None and not len(l) == length:
                raise ValueError(f"{name} must be of length {length}")

        assert_is_list(self.choice_branches, "ats.choice_branches", self.num_choices)
        for choice,branches in enumerate(self.choice_branches):
            assert_is_list(branches, f"ats.choice_branches[{choice}]")
            if not len(branches) > 0:
                raise ValueError(f"ats.choice_branches[{choice}] must be a non-empty list")


        assert_is_list(self.initial_states, "ats.initial_states")
        assert_is_list(self.branch_to_target, "ats.branch_to_target")
        assert_is_list(self.branch_to_value, "ats.branch_to_value")

    def choice_successors(self, choice: int) -> set:
        successors = set()
        for branch in self.choice_branches[choice]:
            successors.add(self.branch_to_target[branch])
        return successors

    def state_successors(self, state: int) -> set:
        successors = set()
        for choice in self.state_choices[state]:
            successors.update(self.choice_successors(choice))
        return successors

    def choice_distribution(self, choice: int) -> dict:
        distr = collections.defaultdict(int)
        for branch in self.choice_branches[choice]:
            distr[self.branch_to_target[branch]] += self.branch_to_value[branch]
        return dict(distr)

    def sample_choice(self, state: int) -> int:
        return random.choice(self.state_choices[state])

    def sample_choice_target(self, choice: int) -> int:
        distr = self.choice_distribution(choice)
        target = random.choices(population=list(distr.keys()), weights=list(distr.values()), k=1)[0]
        return target

    def sample_path(self, state=None, length=0):
        if state is None:
            state = random.choice(self.initial_states)
        path = [state]
        for _ in range(length):
            choice = self.sample_choice(state)
            state = self.sample_choice_target(choice)
            path.append(state)
        return path
