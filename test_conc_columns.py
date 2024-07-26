import math
import conc_columns


def test_calc_Pn():
    assert math.isclose(
        conc_columns.calc_Pn(12, 12, 10, 4, 0.44), 1051.712, rel_tol=1e-3
    )
    assert math.isclose(
        conc_columns.calc_Pn(14, 24, 5, 8, 0.79), 1424.272, rel_tol=1e-3
    )


def test_calc_spacing_per_side():
    assert math.isclose(conc_columns.calc_spacing_per_side(24, 2, d_bar=0.75), 19.5)
    assert math.isclose(conc_columns.calc_spacing_per_side(16, 5, d_bar=0.75), 2.875)


def test_generate_bar_coordinates():
    coordinates = conc_columns.generate_bar_coordinates(14, 24, 3, 3)
    assert coordinates[0][0] == -4.75
    assert coordinates[0][1] == 9.75
    assert coordinates[-1][0] == 4.75
    assert coordinates[-1][1] == 0.0


def test_calc_phi():
    tensile_strains = [60 / 29000, 30 / 29000, 0.005, 0, 0.004]
    test_phis = conc_columns.calc_phi(tensile_strains, 60)
    assert math.isclose(test_phis[0], 0.65)
    assert math.isclose(test_phis[1], 0.65)
    assert math.isclose(test_phis[2], 0.9)
    assert math.isclose(test_phis[3], 0.65)
    assert math.isclose(test_phis[4], 0.8147, rel_tol=1e-4)
