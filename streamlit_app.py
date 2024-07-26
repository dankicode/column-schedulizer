import streamlit as st
from io import StringIO
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


import ram_column_schedule as rcs
import conc_columns
import aci_318_14_materials
import rebar

# Import geometry functions for creating rectangular sections
from sectionproperties.pre.library.primitive_sections import rectangular_section
from concreteproperties.pre import add_bar_rectangular_array


## Import analysis section
from concreteproperties.concrete_section import ConcreteSection

st.write("# RAM Column Schedule")

# Invite user to upload the RAM csv file
concrete_design_csv = st.file_uploader(
    "Upload Concrete Design Output From RAM (*.csv)",
    "csv",
    accept_multiple_files=False,
)


if concrete_design_csv is not None:

    stringio = StringIO(concrete_design_csv.getvalue().decode("utf-8"))
    string_data = stringio.readlines()

    parsed_data = []
    for sd in string_data:
        split_data = sd.split(",")
        parsed_data.append(split_data)

    column_data = rcs.extract_RAM_conc_column_data(parsed_data)
    sched_df = rcs.create_full_RAM_concrete_column_schedule(column_data)
    # display the schedule DataFrame
    st.dataframe(sched_df)
    st.divider()

    st.write("# Design Inspection")

    # Select level for inspection
    raw_levels = column_data["level"]
    unique_levels = []
    for rl in raw_levels:
        if rl not in unique_levels:
            unique_levels.append(rl)

    user_level = st.selectbox(
        "Select Level of column to inspect:",
        options=unique_levels,
        index=None,
        placeholder="Select Level",
    )

    # Select location of column for inspection
    grid_locs = column_data["grid_loc"]
    user_grid_loc = st.selectbox(
        "Select the grid location of the column to inspect:",
        options=grid_locs,
        index=None,
        placeholder="Select grid location",
    )

    design_column, geometry_column = st.columns(2)

    with design_column:
        # Extract design values
        IDX = pd.IndexSlice
        designs = sched_df.loc[IDX[user_level, user_grid_loc]]
        designs

    designs_dict = designs.to_dict()

    b = float(designs_dict["size"].split("x")[0].strip())
    h = float(designs_dict["size"].split("x")[-1].strip())
    bar_quantity = int(designs_dict["rebar"].split("-#")[0])
    bar_size = designs_dict["rebar"].split("-")[-1]
    bar_area = rebar.REBAR[bar_size]["As"]
    bar_diam = rebar.REBAR[bar_size]["d_bar"]
    fpc = float(designs_dict["fpc"])

    # Create material, geometry, and analysis with concreteproperties
    conc = aci_318_14_materials.create_concrete_ACI318(fpc)
    steel = aci_318_14_materials.create_rebar_ACI318(60)  # hardcoded fy for now

    col_geom = rectangular_section(h, b, conc).align_center()

    # User must input the rebar count per side
    n_bars_b = st.number_input(
        """The number of bars per side along the x-direction:""",
        min_value=2,
        value="min",
    )
    n_bars_h = st.number_input(
        "The number of bars per side along the y-direction:",
        min_value=2,
        value="min",
    )
    x_spacing = conc_columns.calc_spacing_per_side(b, n_bars_b, d_bar=bar_diam)
    y_spacing = conc_columns.calc_spacing_per_side(h, n_bars_h, d_bar=bar_diam)
    anchor = (-b / 2 + 1.5 + 0.375 + bar_diam / 2, -h / 2 + 1.5 + 0.375 + bar_diam / 2)
    col_geom = add_bar_rectangular_array(
        col_geom,
        bar_area,
        steel,
        n_bars_b,
        x_spacing,
        n_bars_h,
        y_spacing,
        anchor,
        exterior_only=True,
    )

    # Show column geometry with rebar layout
    with geometry_column:
        # st.set_option("deprecation.showPyplotGlobalUse", False)
        st.pyplot(col_geom.plot_geometry().plot())

    # Aanalysis Section
    conc_sec = ConcreteSection(col_geom)
    mx_int_dia = conc_sec.moment_interaction_diagram(theta=0, n_points=100)
    my_int_dia = conc_sec.moment_interaction_diagram(theta=np.pi / 2, n_points=100)

    eps_t_x = []
    eps_t_y = []
    n_x = []
    n_y = []
    m_x = []
    m_y = []

    # Get axial and moment about x
    for result in mx_int_dia.results:
        dn = round(result.d_n, 3)
        if dn > 24:  # REPLACE WITH LARGEST COLUMN DIM IN DIRECTION OF ANALYSIS
            dn = 24  # REPLACE WITH LARGEST COLUMN DIM IN DIRECTION OF ANALYSIS
        ku = round(result.k_u, 3)
        if dn > 0.1:
            tensile_strain = 0.003 * (dn / ku - dn) / dn
        else:
            tensile_strain = 0.1  # ARBITRARILY LARGE STRAIN

        eps_t_x.append(tensile_strain)
        n_x.append(result.n)
        m_x.append(result.m_x)

    # Get moment about y
    for result in my_int_dia.results:
        dn = round(result.d_n, 3)
        if dn > 24:  # REPLACE WITH LARGEST COLUMN DIM IN DIRECTION OF ANALYSIS
            dn = 24  # REPLACE WITH LARGEST COLUMN DIM IN DIRECTION OF ANALYSIS
        ku = round(result.k_u, 3)
        if dn > 0.1:
            tensile_strain = 0.003 * (dn / ku - dn) / dn
        else:
            tensile_strain = 0.1  # ARBITRARILY LARGE STRAIN

        eps_t_y.append(tensile_strain)
        n_y.append(result.n)
        m_y.append(result.m_y)

    phi_x = np.asarray(conc_columns.calc_phi(eps_t_x))
    phi_y = np.asarray(conc_columns.calc_phi(eps_t_y))

    m_x = np.asarray(m_x)
    m_y = np.asarray(m_y)
    n_x = np.asarray(n_x)
    n_y = np.asarray(n_y)

    pu = float(designs_dict["pu"])
    mu_x_top = float(designs_dict["mu_x_top"])
    mu_x_bot = float(designs_dict["mu_x_bot"])
    mu_y_top = float(designs_dict["mu_y_top"])
    mu_y_bot = float(designs_dict["mu_y_bot"])

    # Plot Moment Interaction Diagram about x
    phi_Pnx = phi_x * n_x
    phi_Mnx = phi_x * m_x / 12  # kip-ft
    phi_Pn_max = 0.65 * conc_columns.calc_Pn(b, h, fpc, bar_quantity, bar_area)

    fig, ax = plt.subplots()
    ax.plot(phi_Mnx, phi_Pnx)
    ax.plot(max(abs(mu_x_top), abs(mu_x_bot)), pu, "x")
    ax.annotate(
        f"{max(abs(mu_x_top), abs(mu_x_bot))}, {pu}",
        (max(abs(mu_x_top), abs(mu_x_bot)), pu),
        xytext=(0.01, 0.7),
        textcoords="axes fraction",
        va="top",
        ha="left",
        arrowprops=dict(facecolor="red", shrink=0.05),
    )
    ax.set_xlabel("phi * Mn_x")
    ax.set_ylabel("phi * Pn")
    ax.set_title("Moment Interaction Diagram (about x)")
    ax.axhline(y=phi_Pn_max)
    ax.grid()
    plt.xticks(np.arange(min(phi_Mnx), max(phi_Mnx) + 50, 50))
    plt.yticks(np.arange(100 * round(min(phi_Pnx / 100)), max(phi_Pnx), 250))
    st.pyplot(fig.tight_layout())

    # Plot Moment Interaction Diagram about y
    phi_Pny = phi_y * n_y
    phi_Mny = phi_y * m_y / -12  # kip-ft
    fig, ax = plt.subplots()
    ax.plot(phi_Mny, phi_Pny)
    ax.plot(max(abs(mu_y_top), abs(mu_y_bot)), pu, "x")
    ax.annotate(
        f"{max(abs(mu_y_top), abs(mu_y_bot))}, {pu}",
        (max(abs(mu_y_top), abs(mu_y_bot)), pu),
        xytext=(0.01, 0.7),
        textcoords="axes fraction",
        va="top",
        ha="left",
        arrowprops=dict(facecolor="red", shrink=0.05),
    )
    ax.set_xlabel("phi * Mn_y")
    ax.set_ylabel("phi * Pn")
    ax.set_title("Moment Interaction Diagram (about y)")
    ax.axhline(y=phi_Pn_max)
    ax.grid()
    plt.xticks(np.arange(min(phi_Mny), max(phi_Mny) + 50, 50))
    plt.yticks(np.arange(100 * round(min(phi_Pny / 100)), max(phi_Pny), 250))
    st.pyplot(fig.tight_layout())

    st.divider()

    st.write("## Quick Calculator")

    st.write("Calculates Phi*Pn for a nonslender column")
    num_bars = st.number_input("Rebar Quantity", min_value=4, value="min")
    # rebar_size = st.text_input("Rebar Size")
    rebar_area = st.number_input("Area of one bar", min_value=0.11, value=0.44)
    fpc = st.number_input("f'c", min_value=3, value=5)
    col_width = st.number_input("Column Width", min_value=6, value=12)
    col_depth = st.number_input("Column Depth", min_value=6, value=12)

    phi_pn = 0.65 * conc_columns.calc_Pn(
        col_width, col_depth, fpc, num_bars, rebar_area
    )
    area_steel_pct = num_bars * rebar_area / (col_width * col_depth)

    st.latex(rf"\large \phi P_n = {round(phi_pn, 2)}")
    st.markdown(f"Column is {round(area_steel_pct * 100, 3)}% reinforced.")
