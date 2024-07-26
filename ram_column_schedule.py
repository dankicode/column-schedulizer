import pandas as pd


def extract_RAM_conc_column_data(
    raw_data: list[str], debug: bool = False
) -> dict[str, list[str]]:
    """
    Returns a dictionary of relevant column design data from the RAM Concrete
    Column "Column Design" csv.
    """

    level = []
    grid_loc = []
    size = []
    rebar = []
    fpc = []
    lux = []
    luy = []
    kx = []
    ky = []
    pu = []
    mu_x_top = []
    mu_y_top = []
    mu_x_bot = []
    mu_y_bot = []

    for idx, row in enumerate(raw_data):
        # keys for nested dict
        if "Level." in row:
            level.append(row[1])
        if "Grid Location:." in row:
            grid_loc.append(row[-1])

        # corresponding values for above keys
        if "Size:." in row:
            item = row[1].split("  ")[0].strip()
            size.append(item)
        if "Longitudinal:." in row:
            rebar.append(row[1].strip().split(" ")[0])
        if "f'c (ksi):." in row:
            fpc.append(row[1].strip())
        if "Unbraced Length (ft)." in row:
            lux.append(row[1])
            luy.append(row[2])
        if "K." in row:
            kx.append(row[1].strip())
            ky.append(row[2].strip())
        if "Axial" in row:
            pu.append(row[-1])
        if "Moment" in row and "Top" in row:
            mu_x_top.append(row[-1].strip())
            mu_y_top.append(raw_data[idx + 1][-1].strip())
        if "Moment" in row and "Bottom" in row:
            mu_x_bot.append(row[-1].strip())
            mu_y_bot.append(raw_data[idx + 1][-1].strip())

    column_data = {
        "level": level,
        "grid_loc": grid_loc,
        "size": size,
        "rebar": rebar,
        "fpc": fpc,
        "lux": lux,
        "luy": luy,
        "kx": kx,
        "ky": ky,
        "pu": pu,
        "mu_x_top": mu_x_top,
        "mu_y_top": mu_y_top,
        "mu_x_bot": mu_x_bot,
        "mu_y_bot": mu_y_bot,
    }
    if debug:
        print(
            f"level: {len(level)}",
            f"grid_loc: {len(grid_loc)}",
            f"size: {len(size)}",
            f"rebar: {len(rebar)}",
            f"fpc: {len(fpc)}",
            f"lux: {len(lux)}",
            f"luy: {len(luy)}",
            f"kx: {len(kx)}",
            f"ky: {len(ky)}",
            f"pu: {len(pu)}",
            f"mu_x_top: {len(mu_x_top)}",
            f"mu_y_top: {len(mu_y_top)}",
            f"mu_x_bot: {len(mu_x_bot)}",
            f"mu_y_bot: {len(mu_y_bot)}",
        )

    return column_data


def create_full_RAM_concrete_column_schedule(
    column_data: dict[str, list[str]],
    xlsx: bool = False,
    output_filename: str = "RAM_Concrete_Column_Schedule.xlsx",
) -> pd.DataFrame:
    """
    Returns a column schedule from the dictionary created from the
    extract_RAM_conc_column_data() function for the streamlit app.

    If xlsx = True, it will also produce an Excel file.
    """
    levels_and_loc_dict = {
        k: column_data[k] for k in ("level", "grid_loc") if k in column_data
    }
    col_sched_dict = {
        k: column_data[k]
        for k in (
            "size",
            "rebar",
            "fpc",
            "pu",
            "mu_x_top",
            "mu_x_bot",
            "mu_y_top",
            "mu_y_bot",
        )
        if k in column_data
    }

    mi_idx = pd.MultiIndex.from_frame(pd.DataFrame(levels_and_loc_dict))
    col_sched_df = pd.DataFrame(col_sched_dict)
    col_sched_df.index = mi_idx

    col_sched_df = col_sched_df.transpose()

    final = []
    for story in pd.Series(column_data["level"]).unique():
        story_df = col_sched_df.loc[:, story].copy()
        story_df["story"] = story
        final.append(story_df)
    schedule_df = pd.concat(final)

    schedule_df = schedule_df.reindex(schedule_df.columns.sort_values(), axis=1)
    story = schedule_df.story
    schedule_df = schedule_df.drop(columns=["story"])
    schedule_df.insert(loc=0, column="story", value=story)
    schedule_df = schedule_df.reset_index().set_index(["story", "index"])
    schedule_df.index.names = ["story", "designs"]

    if xlsx:
        schedule_df.to_excel(output_filename)

    return schedule_df
