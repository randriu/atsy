import pytest

import atsy


def test_ats_parser():
    ats = atsy.from_umb("data/nand-20-1.tar.gz")
    assert ats.choice_successors(50) == set([54])
    assert ats.state_successors(50) == set([54])
    assert ats.sample_choice_target(50) in [54]
