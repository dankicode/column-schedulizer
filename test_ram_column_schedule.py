import ram_column_schedule as rcs

TEST_RAW_DATA = [
    ["Level.", "1st Floor"],
    ["Grid Location:.", "A-1"],
    ["Size:.", "14x24   "],
    ["Longitudinal:.", "12-#8"],
    ["f'c (ksi):.", "   10"],
    ["Unbraced Length (ft).", "10", "10"],
    ["K.", "1.0", "1.0"],
    ["Axial", "nothing", "nothing", "900"],
    ["Moment", "Top", "-100"],
    ["Moment", "Bottom", "-200"],
    ["test", "Bottom", "-300"],
]


def test_extract_RAM_conc_column_data():
    test_dict = rcs.extract_RAM_conc_column_data(TEST_RAW_DATA)
    assert test_dict["level"] == ["1st Floor"]
    assert test_dict["grid_loc"] == ["A-1"]
    assert test_dict["size"] == ["14x24"]
    assert test_dict["rebar"] == ["12-#8"]
    assert test_dict["kx"] == test_dict["ky"] == ["1.0"]
    assert test_dict["pu"] == ["900"]
    assert test_dict["mu_x_top"] == ["-100"]
    assert test_dict["mu_y_top"] == ["-200"]
    assert test_dict["mu_x_bot"] == ["-200"]
    assert test_dict["mu_y_bot"] == ["-300"]


def test_create_full_RAM_concrete_column_schedule():
    test_dict = rcs.extract_RAM_conc_column_data(TEST_RAW_DATA)
    test_schedule = rcs.create_full_RAM_concrete_column_schedule(test_dict)

    assert test_schedule.loc[:, "A-1"].iloc[0] == "14x24"
    assert test_schedule.loc[:, "A-1"].iloc[1] == "12-#8"
    assert test_schedule.loc[:, "A-1"].iloc[2] == "10"
    assert test_schedule.loc[:, "A-1"].iloc[3] == "900"
    assert test_schedule.loc[:, "A-1"].iloc[4] == "-100"
    assert test_schedule.loc[:, "A-1"].iloc[5] == "-200"
    assert test_schedule.loc[:, "A-1"].iloc[6] == "-200"
    assert test_schedule.loc[:, "A-1"].iloc[7] == "-300"
