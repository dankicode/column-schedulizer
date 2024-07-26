from eng_module import rebar


MAX_COL_VERT_BAR_SPACING = 6  # inches, c/c (default)
MIN_COL_VERT_BAR_DIA = rebar.N6.d_bar  # #6 bar minimum (default)


def calc_Pn(
    b: float,
    h: float,
    fpc: float,
    num_bars: int,
    bar_area: float,
    fy: float = 60,
    tie_type: str = "other",
) -> float:
    """
    Calculates the nominal axial capacity of a column, not considering
    slenderness per ACI 318-14 22.4.2

    Args:
    b: width of column in inches
    h: height of column in inches
    fpc: f'c in ksi
    num_bars: number of vertical rebar
    bar_area: area of one of the vertical rebar in sq. inches
    fy: yield stress of rebar
    tie_type: either 'other' or 'spiral'
    """
    gross_area = b * h
    rebar_area = num_bars * bar_area
    p_0 = 0.85 * fpc * (gross_area - rebar_area) + fy * rebar_area

    if tie_type == "other":
        max_axial_strength = 0.8 * p_0
    if tie_type == "spiral":
        max_axial_strength = 0.85 * p_0
    return max_axial_strength


def calc_spacing_per_side(
    col_dim: float,
    n_bars: int,
    cover: float = 1.5,
    d_tie: float = rebar.N3.d_bar,
    d_bar: float = MIN_COL_VERT_BAR_DIA,
) -> float:
    """
    Calculates the center to center spacing of equally spaced rebar on a
    particular side of a column.
    """
    if n_bars == 1:
        spacing_cc = (col_dim - 2 * cover - 2 * d_tie - d_bar) / (n_bars + 2)
        return spacing_cc

    spacing_cc = (col_dim - 2 * cover - 2 * d_tie - d_bar) / (n_bars - 1)

    return spacing_cc


def generate_bar_coordinates(
    b: float,
    h: float,
    n_bars_b: int,
    n_bars_h: int,
    cover: float = 1.5,
    d_tie: float = rebar.N3.d_bar,
    d_bar: float = MIN_COL_VERT_BAR_DIA,
) -> list[list[float]]:
    """
    Returns a nested list of x and y coordinates of rebar in a rectangular
    column geometry. (0, 0) is the centroid of the section.
    """

    sx = calc_spacing_per_side(b, n_bars_b)
    sy = calc_spacing_per_side(h, n_bars_h)

    x_coords = []
    y_coords = []
    x1 = -b / 2 + cover + d_tie + d_bar / 2
    y1 = h / 2 - cover - d_tie - d_bar / 2

    # top and bottom coordinates contain the corners!
    # top coordinates
    for i in range(n_bars_b):
        x_coords.append(x1 + i * sx)
        y_coords.append(y1)

    # bottom coordinates
    for i in range(n_bars_b):
        x_coords.append(x1 + i * sx)
        y_coords.append(-y1)

    # left coordinates
    for i in range(1, n_bars_h - 1):
        x_coords.append(x1)
        y_coords.append(y1 - i * sy)

    # right coordinates
    for i in range(1, n_bars_h - 1):
        x_coords.append(-x1)
        y_coords.append(y1 - i * sy)

    return list([list(i) for i in zip(x_coords, y_coords)])
    # return x_coords, y_coords


def calc_phi(
    tensile_strains: list[float],
    fy: float = 60,
    Es: float = 29000,
    reinf_type: str = "other",
) -> list[float]:
    """
    Returns a list of phi values for the given tensile strains per ACI 318-14.
    """
    tensile_yield_strain = fy / Es
    phis = []
    if reinf_type == "other":
        for ts in tensile_strains:
            if ts <= tensile_yield_strain:
                phi = 0.65
                phis.append(phi)
            elif ts > tensile_yield_strain and ts < 0.005:
                phi = 0.65 + 0.25 * (ts - tensile_yield_strain) / (
                    0.005 - tensile_yield_strain
                )
                phis.append(phi)
            elif ts >= 0.005:
                phi = 0.9
                phis.append(phi)
    else:
        print("Spiral ties not yet implemented!")
    return phis
