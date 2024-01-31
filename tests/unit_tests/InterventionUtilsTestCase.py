import unittest
from ..utils import *
from pyvene.models.intervention_utils import _do_intervention_by_swap
from pyvene.models.interventions import VanillaIntervention
from pyvene.models.interventions import CollectIntervention


class InterventionUtilsTestCase(unittest.TestCase):
    def test_vanilla_intervention_positive(self):
        intervention = VanillaIntervention(embed_dim=2)
        base = torch.arange(36).view(2, 3, 6)
        source = torch.arange(36, 72).view(2, 3, 6)
        output = intervention(base, source)
        golden = torch.tensor(
            [
                [
                    [36, 37, 2, 3, 4, 5],
                    [42, 43, 8, 9, 10, 11],
                    [48, 49, 14, 15, 16, 17],
                ],
                [
                    [54, 55, 20, 21, 22, 23],
                    [60, 61, 26, 27, 28, 29],
                    [66, 67, 32, 33, 34, 35],
                ],
            ]
        )
        self.assertTrue(torch.allclose(golden, output))

    def test_vanilla_intervention_negative(self):
        intervention = VanillaIntervention(embed_dim=2)
        base = torch.arange(36).view(2, 3, 6)
        # Shape cannot broadcast
        source = torch.arange(36, 42).view(1, 6)
        try:
            output = intervention(base, source)
        except ValueError:
            pass

    def test_vanilla_intervention_subspace_positive(self):
        intervention = VanillaIntervention()
        base = torch.arange(36).view(2, 3, 6)
        source = torch.arange(36, 72).view(2, 3, 6)
        output = intervention(base, source, subspaces=[[1, 0], [0, 1], [1, 2]])
        golden = torch.tensor(
            [
                [
                    [36, 37, 2, 3, 4, 5],
                    [42, 43, 8, 9, 10, 11],
                    [12, 49, 50, 15, 16, 17],
                ],
                [
                    [54, 55, 20, 21, 22, 23],
                    [60, 61, 26, 27, 28, 29],
                    [30, 67, 68, 33, 34, 35],
                ],
            ]
        )

        self.assertTrue(torch.allclose(golden, output))

    def test_vanilla_intervention_subspace_partition_positive(self):
        # Both [0,2],[2,4],[4,6], and [0,1],[2,3],[4,5] works
        intervention = VanillaIntervention(subspace_partition=[[0, 2], [2, 4], [4, 6]])
        base = torch.arange(36).view(2, 3, 6)
        source = torch.arange(36, 72).view(2, 3, 6)
        output = intervention(base, source, subspaces=[[1, 0], [0, 1], [1, 2]])
        golden = torch.tensor(
            [
                [
                    [36, 37, 38, 39, 4, 5],
                    [42, 43, 44, 45, 10, 11],
                    [12, 13, 50, 51, 52, 53],
                ],
                [
                    [54, 55, 56, 57, 22, 23],
                    [60, 61, 62, 63, 28, 29],
                    [30, 31, 68, 69, 70, 71],
                ],
            ]
        )

        self.assertTrue(torch.allclose(golden, output))

    def test_vanilla_intervention_subspace_negative(self):
        intervention = VanillaIntervention()
        base = torch.arange(36).view(2, 3, 6)
        source = torch.arange(36, 72).view(2, 3, 6)
        try:
            # 6 is out of index bounds
            intervention(base, source, subspaces=[1, 6])
        except IndexError:
            pass

    def test_vanilla_intervention_subspace_partition_negative(self):
        # Subspace partitions are not equal
        intervention = VanillaIntervention(subspace_partition=[[0, 1, 2], [3, 4], [5]])
        base = torch.arange(36).view(2, 3, 6)
        source = torch.arange(36, 72).view(2, 3, 6)
        try:
            intervention(base, source)
        except ValueError:
            pass

    def test_vanilla_intervention_broadcast_positive(self):
        intervention = VanillaIntervention(subspace_partition=[[0, 1], [2, 3], [4, 5]])
        base = torch.arange(36).view(2, 3, 6)
        source = torch.arange(36, 42).view(6)
        output = intervention(base, source, subspaces=[[1, 0], [0, 1], [1, 2]])
        golden = torch.tensor(
            [
                [
                    [36, 37, 38, 39, 4, 5],
                    [36, 37, 38, 39, 10, 11],
                    [12, 13, 38, 39, 40, 41],
                ],
                [
                    [36, 37, 38, 39, 22, 23],
                    [36, 37, 38, 39, 28, 29],
                    [30, 31, 38, 39, 40, 41],
                ],
            ]
        )

    def test_vanilla_intervention_fast_positive(self):
        intervention = VanillaIntervention(
            subspace_partition=[[0, 1], [2, 3], [4, 5]], use_fast=True
        )
        base = torch.arange(36).view(2, 3, 6)
        source = torch.arange(36, 42).view(6)
        output = intervention(base, source, subspaces=[[1, 0], [0, 1], [1, 2]])
        golden = torch.tensor(
            [
                [
                    [36, 37, 38, 39, 4, 5],
                    [36, 37, 38, 39, 10, 11],
                    [36, 37, 38, 39, 14, 15],
                ],
                [
                    [36, 37, 38, 39, 22, 23],
                    [36, 37, 38, 39, 28, 29],
                    [36, 37, 38, 39, 34, 35],
                ],
            ]
        )

    def test_collect_intervention_negative(self):
        intervention = CollectIntervention(subspace_partition=[[0, 1], [2, 3], [4, 5]])
        base = torch.arange(36).view(2, 3, 6)
        source = torch.arange(36, 42).view(6)
        try:
            intervention(base, source, subspaces=[[1, 0], [0, 1], [1, 2]])
        except AssertionError:
            pass

    def test_collect_intervention_positive(self):
        intervention = CollectIntervention(subspace_partition=[[0, 1], [2, 3], [4, 5]])
        base = torch.arange(36).view(2, 3, 6)
        output = intervention(base, None, subspaces=[[1, 0], [0, 1], [1, 2]])
        # `Fast` would treat all subspaces as the same as the first subspace
        golden = torch.tensor(
            [
                [[0, 1, 2, 3], [6, 7, 8, 9], [14, 15, 16, 17]],
                [[18, 19, 20, 21], [24, 25, 26, 27], [32, 33, 34, 35]],
            ]
        )

    def test_bas_intervention_positive(self):
        # TODO: implement
        pass

    def test_low_rank_rotated_space_positive(self):
        # TODO: implement
        pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(
        InterventionUtilsTestCase("test_vanilla_intervention_subspace_positive")
    )
    suite.addTest(InterventionUtilsTestCase("test_vanilla_intervention_positive"))
    suite.addTest(InterventionUtilsTestCase("test_vanilla_intervention_negative"))
    suite.addTest(
        InterventionUtilsTestCase(
            "test_vanilla_intervention_subspace_partition_positive"
        )
    )
    suite.addTest(
        InterventionUtilsTestCase("test_vanilla_intervention_broadcast_positive")
    )
    suite.addTest(
        InterventionUtilsTestCase("test_vanilla_intervention_subspace_negative")
    )
    suite.addTest(
        InterventionUtilsTestCase(
            "test_vanilla_intervention_subspace_partition_negative"
        )
    )
    suite.addTest(InterventionUtilsTestCase("test_vanilla_intervention_fast_positive"))
    suite.addTest(InterventionUtilsTestCase("test_collect_intervention_positive"))
    suite.addTest(InterventionUtilsTestCase("test_collect_intervention_negative"))

    # TODO: Add tests to other interventions
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
