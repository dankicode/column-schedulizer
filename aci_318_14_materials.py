# Import stress/strain profiles
from concreteproperties.stress_strain_profile import (
    ConcreteLinearNoTension,
    RectangularStressBlock,
    SteelElasticPlastic,
)

# Import materials
from concreteproperties.material import Concrete, SteelBar


def calculate_beta_1(fpc: float) -> float:
    """
    Calculate Beta_1 in accordance with ACI 318-14 Table 22.2.2.4.3.

    Args:
    fpc: f'c in ksi
    """
    if fpc >= 2.5 and fpc <= 4.0:
        beta_1 = 0.85
    elif fpc > 4.0 and fpc < 8.0:
        beta_1 = 0.85 - (0.05 * (fpc - 4))
    elif fpc >= 8.0:
        beta_1 = 0.65
    else:
        print("f'c is less than 2.5ksi - assuming beta_1 = 0.85.")
        return 0.85
    return beta_1


def calc_modulus_of_rupture(fpc: float, lambda_agg: float = 1.0) -> float:
    """
    Calculate modulus of rupture, f_r in accordance with ACI 318.

    Args:
    fpc: f'c in ksi
    lambda_agg: lightweight aggregate factor = 1.0 for normal weight
    """
    fr = 7.5 * lambda_agg * ((fpc * 1000) ** 0.5) / 1000  # ksi
    return fr


def calc_concrete_elastic_modulus(fpc: float, wc: float) -> float:
    Ec = 33 * ((wc * 1000) ** 1.5) * ((fpc * 1000) ** 0.5) / 1000  # ksi
    return Ec


def create_concrete_ACI318(fpc: float, wc: float = 0.15, eps_cu: float = 0.003):
    """
    Returns a concreteproperties concrete material with values
    calculated per ACI 318-14.

    Args:
    fpc: f'c in ksi
    wc: unit weight of concrete in kcf
    eps_cu: ultimate crushing strain of concrete"""

    Ec = calc_concrete_elastic_modulus(fpc, wc)
    # only takes compression and stress is linear
    concrete_service = ConcreteLinearNoTension(
        elastic_modulus=Ec, ultimate_strain=eps_cu, compressive_strength=0.85 * fpc
    )

    # Ultimate stress-strain profile
    beta_1 = calculate_beta_1(fpc)
    concrete_ultimate = RectangularStressBlock(
        compressive_strength=fpc, alpha=0.85, gamma=beta_1, ultimate_strain=eps_cu
    )

    # Define the concrete material
    fr = calc_modulus_of_rupture(fpc)
    concrete = Concrete(
        name=f"{fpc} ksi Concrete",
        density=wc / (12**3),  # ksi
        stress_strain_profile=concrete_service,
        colour="lightgrey",
        ultimate_stress_strain_profile=concrete_ultimate,
        flexural_tensile_strength=fr,
    )
    return concrete


def create_rebar_ACI318(
    fy: float, Es: float = 29000.0, eps_fracture: float = 0.3, density: float = 0.49
):
    """
    Returns a concreteproperties rebar material.

    Args:
    fy: yield strength of rebar in ksi
    Es: elastic modulus in ksi
    eps_fracture: fracture strain of rebar (MADE UP VALUE.. CONFIRM WITH SR OR MA)
    density: unit weight of steel in kcf
    """
    # Rebar stress-strain profile
    steel_elastic_plastic = SteelElasticPlastic(
        yield_strength=fy, elastic_modulus=Es, fracture_strain=eps_fracture
    )

    # Rebar material
    # SteelBar will lump the areas at their centroid
    steel = SteelBar(
        name=f"Grade {fy} Rebar",
        density=density / (12**3),  # ksi
        stress_strain_profile=steel_elastic_plastic,
        colour="black",
    )

    return steel
