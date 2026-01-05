from PyQt5 import QtWidgets, QtCore

def create_settings_group(on_unit_changed):
    group = QtWidgets.QGroupBox("Settings")
    layout = QtWidgets.QHBoxLayout()
    mm = QtWidgets.QRadioButton("mm")
    inch = QtWidgets.QRadioButton("in")
    mm.setChecked(True)
    mm.toggled.connect(on_unit_changed)
    layout.addWidget(mm)
    layout.addWidget(inch)
    group.setLayout(layout)
    return group, mm, inch

def create_spring_group(
        q_spring_id,
        q_spring_wire_diameter,
        q_spring_free_length,
        q_spring_rate,
        q_spring_bind_length
        ):
    spring_group   = QtWidgets.QGroupBox("Spring")
    spring_layout  = QtWidgets.QFormLayout()

    lbl = QtWidgets.QLabel("Inner diameter (mm):")
    lbl.setObjectName("Inner diameter")
    spring_layout.addRow(lbl, q_spring_id)

    lbl = QtWidgets.QLabel("Wire diameter (mm):")
    lbl.setObjectName("Wire diameter")
    spring_layout.addRow(lbl, q_spring_wire_diameter)

    lbl = QtWidgets.QLabel("Spring free length (mm):")
    lbl.setObjectName("Spring free length")
    spring_layout.addRow(lbl, q_spring_free_length)

    lbl = QtWidgets.QLabel("Spring Rate (N/mm):")
    lbl.setObjectName("Spring Rate")
    spring_layout.addRow(lbl, q_spring_rate)

    lbl = QtWidgets.QLabel("Length at bind (mm):")
    lbl.setObjectName("Length at bind")
    spring_layout.addRow(lbl, q_spring_bind_length)

    spring_group.setLayout(spring_layout)
    return spring_group

def create_damper_group(
        q_damper_free_length,
        q_damper_comp_length,
        q_damper_body_length,
        q_damper_body_diameter,
        q_damper_shaft_diameter,
        q_body_threaded_length,
        ):
    damper_group  = QtWidgets.QGroupBox("Damper")
    damper_layout = QtWidgets.QFormLayout()

    lbl = QtWidgets.QLabel("Damper free length (mm):")
    lbl.setObjectName("Damper free length")
    damper_layout.addRow(lbl, q_damper_free_length)

    lbl = QtWidgets.QLabel("Compressed length (mm):")
    lbl.setObjectName("Compressed length")
    damper_layout.addRow(lbl, q_damper_comp_length)

    lbl = QtWidgets.QLabel("Body length (mm):")
    lbl.setObjectName("Body length")
    damper_layout.addRow(lbl, q_damper_body_length)

    lbl = QtWidgets.QLabel("Body diameter (mm):")
    lbl.setObjectName("Body diameter")
    damper_layout.addRow(lbl, q_damper_body_diameter)

    lbl = QtWidgets.QLabel("Shaft diameter (mm):")
    lbl.setObjectName("Shaft diameter")
    damper_layout.addRow(lbl, q_damper_shaft_diameter)

    lbl = QtWidgets.QLabel("Body threaded length (mm):")
    lbl.setObjectName("Body threaded length")
    damper_layout.addRow(lbl, q_body_threaded_length)

    damper_group.setLayout(damper_layout)
    return damper_group

def create_helper_spring_group(
        on_helper_toggled,
        use_helper,
        q_helper_outer_diameter,
        q_helper_inner_diameter,
        q_helper_thickness,
        q_helper_inner_height,
        q_helper_spring_id,
        q_helper_spring_od,
        q_helper_spring_free_length,
        q_helper_spring_rate,
        q_helper_spring_bind_length,
        ):
    # Helper spring group
    helper_group  = QtWidgets.QGroupBox("Helper spring")
    helper_layout = QtWidgets.QFormLayout()

    helper_chk = QtWidgets.QCheckBox("Add helper spring")
    helper_layout.addRow(helper_chk)
    helper_chk.toggled.connect(on_helper_toggled)

    helper_above = QtWidgets.QRadioButton("Above main spring")
    helper_below = QtWidgets.QRadioButton("Below main spring")
    helper_above.setChecked(True)
    # self.helper_above.toggled.connect(self.helper_change) #TODO

    rb_container = QtWidgets.QWidget()
    rb_layout    = QtWidgets.QHBoxLayout(rb_container)
    rb_layout.setContentsMargins(0,0,0,0)
    rb_layout.addWidget(helper_above)
    rb_layout.addWidget(helper_below)
    helper_layout.addRow(rb_container)   # place the two buttons in one row

    # Helper perch dimensions
    lbl = QtWidgets.QLabel("Helper perch outer diameter (mm):")
    lbl.setObjectName("Helper perch outer diameter")
    helper_layout.addRow(lbl, q_helper_outer_diameter)

    lbl = QtWidgets.QLabel("Helper perch inner diameter (mm):")
    lbl.setObjectName("Helper perch inner diameter")
    helper_layout.addRow(lbl, q_helper_inner_diameter)

    lbl = QtWidgets.QLabel("Helper perch thickness (mm):")
    lbl.setObjectName("Helper perch thickness")
    helper_layout.addRow(lbl, q_helper_thickness)

    lbl = QtWidgets.QLabel("Helper perch inner height (mm):")
    lbl.setObjectName("Helper perch inner height")
    helper_layout.addRow(lbl, q_helper_inner_height)

    # Helper spring dimensions

    lbl = QtWidgets.QLabel("Helper spring inner diameter (mm):")
    lbl.setObjectName("Helper spring inner diameter")
    helper_layout.addRow(lbl, q_helper_spring_id)

    lbl = QtWidgets.QLabel("Helper spring outer diameter (mm):")
    lbl.setObjectName("Helper spring inner diameter")
    helper_layout.addRow(lbl, q_helper_spring_od)

    lbl = QtWidgets.QLabel("Helper spring free length (mm):")
    lbl.setObjectName("Helper spring free length")
    helper_layout.addRow(lbl, q_helper_spring_free_length)

    lbl = QtWidgets.QLabel("Helper spring rate (N/mm):")
    lbl.setObjectName("Helper spring rate")
    helper_layout.addRow(lbl, q_helper_spring_rate)

    lbl = QtWidgets.QLabel("Length at bind (mm):")
    lbl.setObjectName("Length at bind")
    helper_layout.addRow(lbl, q_helper_spring_bind_length)

    for w in (
        helper_above,
        helper_below,
        q_helper_outer_diameter,
        q_helper_inner_diameter,
        q_helper_thickness,
        q_helper_inner_height,
        q_helper_spring_id,
        q_helper_spring_od,
        q_helper_spring_free_length,
        q_helper_spring_rate,
        q_helper_spring_bind_length
    ):
        w.setEnabled(use_helper)

    helper_group.setLayout(helper_layout)
    return helper_group, helper_chk, helper_above, helper_below

def create_bump_stop_group(
        on_bump_toggled,
        use_bump,
        q_bump_height,
        q_bump_diameter,
        q_bump_rate
        ):
    bump_group  = QtWidgets.QGroupBox("Bump Stop")
    bump_layout = QtWidgets.QFormLayout()

    bump_chk = QtWidgets.QCheckBox("Add bump stop")
    bump_layout.addRow(bump_chk)
    bump_chk.toggled.connect(on_bump_toggled)

    radio_bump_ext = QtWidgets.QRadioButton("External")
    radio_bump_int = QtWidgets.QRadioButton("Internal")
    radio_bump_ext.setChecked(True)
    # self.radio_bump_ext.toggled.connect(self.bump_change) #TODO

    bump_rb_container = QtWidgets.QWidget()
    bump_rb_layout    = QtWidgets.QHBoxLayout(bump_rb_container)
    bump_rb_layout.setContentsMargins(0,0,0,0)
    bump_rb_layout.addWidget(radio_bump_ext)
    bump_rb_layout.addWidget(radio_bump_int)
    bump_layout.addRow(bump_rb_container)   # place the two buttons in one row

    lbl = QtWidgets.QLabel("Bump stop height (mm):")
    lbl.setObjectName("Bump stop height")
    bump_layout.addRow(lbl, q_bump_height)

    lbl = QtWidgets.QLabel("Bump stop outer diameter (mm):")
    lbl.setObjectName("Bump stop outer diameter")
    bump_layout.addRow(lbl, q_bump_diameter)

    lbl = QtWidgets.QLabel("Bump stop spring rate (mm):")
    lbl.setObjectName("Bump stop spring rate")
    bump_layout.addRow(lbl, q_bump_rate)

    for w in (
        radio_bump_ext,
        radio_bump_int,
        q_bump_height,
        q_bump_diameter,
        q_bump_rate,
    ):
        w.setEnabled(use_bump)

    bump_group.setLayout(bump_layout)
    return bump_group, bump_chk, radio_bump_ext, radio_bump_int

def create_upper_perch_group(
        q_upper_perch_outer_diameter,
        q_upper_perch_thickness,
        q_upper_perch_tapered_height
        ):
    upper_perch_group  = QtWidgets.QGroupBox("Upper Spring Perch")
    upper_perch_layout = QtWidgets.QFormLayout()

    # Upper perch dimensions
    lbl = QtWidgets.QLabel("Upper perch outer diameter (mm):")
    lbl.setObjectName("Upper perch outer diameter")
    upper_perch_layout.addRow(lbl, q_upper_perch_outer_diameter)

    lbl = QtWidgets.QLabel("Upper perch thickness (mm):")
    lbl.setObjectName("Upper perch thickness")
    upper_perch_layout.addRow(lbl, q_upper_perch_thickness)

    lbl = QtWidgets.QLabel("Helper perch tapered height (mm):")
    lbl.setObjectName("Helper perch tapered height")
    upper_perch_layout.addRow(lbl, q_upper_perch_tapered_height)

    upper_perch_group.setLayout(upper_perch_layout)
    return upper_perch_group

def create_lower_perch_group(
        on_lower_perch_adj_toggled,
        lower_perch_sleeve_chk_toggled,
        q_lower_perch_outer_diameter,
        q_lower_perch_thickness,
        q_lower_perch_sleeve_height,
        q_lower_perch_sleeve_inner_diameter
        ):
    lower_perch_group  = QtWidgets.QGroupBox("Lower Spring Perch")
    lower_perch_layout = QtWidgets.QFormLayout()

    lower_perch_adjustable_chk = QtWidgets.QCheckBox("Adjustable height")
    lower_perch_layout.addRow(lower_perch_adjustable_chk)
    lower_perch_adjustable_chk.toggled.connect(on_lower_perch_adj_toggled)

    lower_perch_sleeve_chk = QtWidgets.QCheckBox("Use coilover conversion sleeve")
    lower_perch_layout.addRow(lower_perch_sleeve_chk)
    lower_perch_sleeve_chk.toggled.connect(lower_perch_sleeve_chk_toggled)

    # Lower perch dimensions
    lbl = QtWidgets.QLabel("Lower perch outer diameter (mm):")
    lbl.setObjectName("Lower perch outer diameter")
    lower_perch_layout.addRow(lbl, q_lower_perch_outer_diameter)

    lbl = QtWidgets.QLabel("Lower perch thickness (mm):")
    lbl.setObjectName("Lower perch thickness")
    lower_perch_layout.addRow(lbl, q_lower_perch_thickness)

    # Coilover conversion sleeve dimensions
    lbl = QtWidgets.QLabel("Sleeve height (mm):")
    lbl.setObjectName("Sleeve height")
    lower_perch_layout.addRow(lbl, q_lower_perch_sleeve_height)

    lbl = QtWidgets.QLabel("Sleeve inner diameter (mm):")
    lbl.setObjectName("Sleeve inner diameter")
    lower_perch_layout.addRow(lbl, q_lower_perch_sleeve_inner_diameter)

    lower_perch_group.setLayout(lower_perch_layout)
    return lower_perch_group, lower_perch_adjustable_chk, lower_perch_sleeve_chk

def create_setup_group(
        q_lower_perch_position
        ):
    setup_group  = QtWidgets.QGroupBox("Setup")
    setup_layout = QtWidgets.QFormLayout()

    flip_damper_chk = QtWidgets.QCheckBox("Flip damper orientation")
    setup_layout.addRow(flip_damper_chk)

    lbl = QtWidgets.QLabel("Spring perch starting point (mm):")
    lbl.setObjectName("Spring perch starting point")
    setup_layout.addRow(lbl, q_lower_perch_position)

    setup_group.setLayout(setup_layout)
    return setup_group, flip_damper_chk
