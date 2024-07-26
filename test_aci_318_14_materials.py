import math
import aci_318_14_materials as aci


def test_calculate_beta_1():
    assert aci.calculate_beta_1(4) == 0.85
    assert aci.calculate_beta_1(6) == 0.75
    assert aci.calculate_beta_1(9) == 0.65


def test_calc_modulus_of_rupture():
    assert math.isclose(aci.calc_modulus_of_rupture(4), 0.474341649)
    assert math.isclose(aci.calc_modulus_of_rupture(10), 0.75)
