import sys
import numpy as np

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QVector3D
import pyqtgraph as pg
import pyqtgraph.opengl as gl

from mesh_utils import *
from physics_utils import *
from ui_panels import *

class CoiloverDesigner(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coilover Tool")
        self.resize(1000, 600)

        # === Left panel: parameter inputs ===
        form = QtWidgets.QFormLayout()

        # text field variables
        self.q_spring_id                    = QtWidgets.QLineEdit("63.5")   # mm
        self.q_spring_wire_diameter         = QtWidgets.QLineEdit("9.6")   # mm
        self.q_spring_free_length           = QtWidgets.QLineEdit("101.6")  # mm
        self.q_spring_rate                  = QtWidgets.QLineEdit("70.04")  # N/mm
        self.q_spring_bind_length           = QtWidgets.QLineEdit("33.83")   # mm

        self.q_damper_free_length           = QtWidgets.QLineEdit("400")  # mm
        self.q_damper_comp_length           = QtWidgets.QLineEdit("250")  # mm
        self.q_damper_body_length           = QtWidgets.QLineEdit("200")  # mm
        self.q_damper_body_diameter         = QtWidgets.QLineEdit("50")   # mm
        self.q_damper_shaft_diameter        = QtWidgets.QLineEdit("20")   # mm
        self.q_body_threaded_length         = QtWidgets.QLineEdit("100")  # mm

        self.use_helper = 0
        self.q_helper_outer_diameter        = QtWidgets.QLineEdit("85")
        self.q_helper_inner_diameter        = QtWidgets.QLineEdit("64")
        self.q_helper_thickness             = QtWidgets.QLineEdit("2.5")
        self.q_helper_inner_height          = QtWidgets.QLineEdit("13")
        self.q_helper_spring_id             = QtWidgets.QLineEdit("57.15") # mm
        self.q_helper_spring_od             = QtWidgets.QLineEdit("73.91") # mm
        self.q_helper_spring_free_length    = QtWidgets.QLineEdit("101.6") # mm
        self.q_helper_spring_rate           = QtWidgets.QLineEdit("2.63")  # N/mm
        self.q_helper_spring_bind_length    = QtWidgets.QLineEdit("11.18") # mm

        self.use_bump = 0
        self.q_bump_height                  = QtWidgets.QLineEdit("25")
        self.q_bump_diameter                = QtWidgets.QLineEdit("50")
        self.q_bump_rate                    = QtWidgets.QLineEdit("50")

        self.q_lower_perch_outer_diameter   = QtWidgets.QLineEdit("87")
        self.q_lower_perch_thickness        = QtWidgets.QLineEdit("13")
        self.q_lower_perch_sleeve_height    = QtWidgets.QLineEdit("56")
        self.q_lower_perch_sleeve_inner_diameter   = QtWidgets.QLineEdit("52")

        self.q_upper_perch_outer_diameter   = QtWidgets.QLineEdit("85")
        self.q_upper_perch_thickness        = QtWidgets.QLineEdit("10")
        self.q_upper_perch_tapered_height   = QtWidgets.QLineEdit("10")

        self.q_lower_perch_position         = QtWidgets.QLineEdit("10")   # mm
        # 87 mm diameter perch

        self.unit = "mm"

        # Settings group
        settings_group, self.radio_mm, self.radio_in = create_settings_group(self.on_unit_changed)

        # Spring group
        spring_group = create_spring_group(
            self.q_spring_id,
            self.q_spring_wire_diameter,
            self.q_spring_free_length,
            self.q_spring_rate,
            self.q_spring_bind_length)

        # Damper group
        damper_group = create_damper_group(
            self.q_damper_free_length,
            self.q_damper_comp_length,
            self.q_damper_body_length,
            self.q_damper_body_diameter,
            self.q_damper_shaft_diameter,
            self.q_body_threaded_length,
            )

        # Helper spring group
        helper_group, self.helper_chk, self.helper_above, self.helper_below = create_helper_spring_group(
            self.on_helper_toggled,
            self.use_helper,
            self.q_helper_outer_diameter,
            self.q_helper_inner_diameter,
            self.q_helper_thickness,
            self.q_helper_inner_height,
            self.q_helper_spring_id,
            self.q_helper_spring_od,
            self.q_helper_spring_free_length,
            self.q_helper_spring_rate,
            self.q_helper_spring_bind_length,
            )

        # Bump stop group
        bump_group, self.bump_chk, self.radio_bump_ext, self.radio_bump_int = create_bump_stop_group(
            self.on_bump_toggled,
            self.use_bump,
            self.q_bump_height,
            self.q_bump_diameter,
            self.q_bump_rate
            )

        # Lower perch group
        lower_perch_group, self.lower_perch_adjustable_chk, self.lower_perch_sleeve_chk = create_lower_perch_group(
            self.on_lower_perch_adj_toggled,
            self.lower_perch_sleeve_chk_toggled,
            self.q_lower_perch_outer_diameter,
            self.q_lower_perch_thickness,
            self.q_lower_perch_sleeve_height,
            self.q_lower_perch_sleeve_inner_diameter
        )

        self.on_lower_perch_adj_toggled(self.lower_perch_adjustable_chk.isChecked())
        self.lower_perch_sleeve_chk_toggled(self.lower_perch_sleeve_chk.isChecked())

        # Upper perch group
        upper_perch_group = create_upper_perch_group(
            self.q_upper_perch_outer_diameter,
            self.q_upper_perch_thickness,
            self.q_upper_perch_tapered_height
        )

        # Setup group
        setup_group, self.flip_damper_chk = create_setup_group(self.q_lower_perch_position)

        # Assemble left‐side layout
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(settings_group)
        left_layout.addWidget(spring_group)
        left_layout.addWidget(damper_group)
        left_layout.addWidget(helper_group)
        left_layout.addWidget(bump_group)
        left_layout.addWidget(lower_perch_group)
        left_layout.addWidget(setup_group)

        # Separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        left_layout.addWidget(separator)

        # Update button
        update_btn = QtWidgets.QPushButton("Update View")
        update_btn.clicked.connect(self.update_view)
        left_layout.addWidget(update_btn, alignment=QtCore.Qt.AlignTop)

        left = QtWidgets.QWidget()
        left.setLayout(left_layout)

        # Make the left scrollable
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(left)

        btn = QtWidgets.QPushButton("Update View")
        btn.clicked.connect(self.update_view)
        form.addRow(btn)

        # === Right panel: 3D view ===
        self.view = gl.GLViewWidget()
        self.view.opts['lightPosition'] = (10, 10, 40)
        self.view.opts['distance'] = 600
        self.view.setBackgroundColor('#181818')

        # Text Overlays
        self.info_label = QtWidgets.QLabel(self.view)
        self.info_label.setWordWrap(True)    # allow multiple lines
        self.info_label.setStyleSheet("""
            color: white;
            background-color: rgba(0,0,0,0);
            font-weight: bold;
        """)
        self.info_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.info_label.move(10, 10)   # 10px from top‐left
        self.info_label.show()

        # bottom‐center help text
        self.help_label = QtWidgets.QLabel(self.view)
        self.help_label.setStyleSheet("""
            color: white;
            background-color: rgba(0,0,0,0);
            font-size: 10pt;
        """)
        self.help_label.setText("Right-click to rotate; Scroll wheel to zoom; Cmd + right-click to pan")
        self.help_label.adjustSize()
        self.help_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.help_label.show()

        # axes for reference
        axis = gl.GLAxisItem()
        axis.setSize(100,100,100)
        self.view.addItem(axis)

        # slider for travel
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setFixedHeight(25)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.animate)

        # layout them
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        right_panel = QtWidgets.QVBoxLayout()

        w = QtWidgets.QWidget()
        w.setLayout(right_panel)
        right_panel.addWidget(self.view)
        right_panel.addWidget(self.slider)
        splitter.addWidget(scroll)
        splitter.addWidget(w)
        # give left:1, right:2 proportion roughly 1/3 : 2/3
        # Give right twice the stretch of left (i.e. ~2/3 of the width)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        # placeholders
        self.spring_mesh = None
        self.body_mesh   = None
        self.shaft_mesh  = None
        self.upper_perch = None
        self.upper_cone  = None
        self.helper_spring_mesh = None

        # Have the camera center on the top of the damper body
        self.view.opts['center'] = QVector3D(0, 0, self.read_length(self.q_damper_body_length))
        self.view.setCameraPosition(
            azimuth=45        # rotate around Z by 0°
        )

        # initial draw
        self.update_view()

    def on_unit_changed(self):
        """
        Re label inputs and convert their numeric values.
        """
        new_unit = "in" if self.radio_in.isChecked() else "mm"
        if new_unit == self.unit:
            return

        # conversion factors
        to_in  = lambda x: x/25.4
        to_mm  = lambda x: x*25.4
        conv   = to_in if new_unit=="in" else to_mm

        # for each (widget, attr_name) in your inputs:
        for widget, label_base in [
            (self.q_spring_id,    "Inner diameter"),
            (self.q_spring_wire_diameter, "Wire diameter"),
            (self.q_spring_free_length,  "Spring free length"),
            (self.q_spring_rate,  "Spring Rate"),
            (self.q_spring_bind_length,  "Length at bind"),
            (self.q_damper_free_length,  "Damper free length"),
            (self.q_damper_comp_length, "Compressed length"),
            (self.q_damper_body_length,  "Body length"),
            (self.q_damper_body_diameter,  "Body diameter"),
            (self.q_damper_shaft_diameter, "Shaft diameter"),
            (self.q_lower_perch_position,  "Spring perch distance"),
        ]:
            # read old value, convert to new unit
            try:
                old_val = float(widget.text())
                new_val = conv(old_val)
                widget.setText(f"{new_val:.3f}")
            except ValueError:
                pass

            # update the form label text
            label = widget.parentWidget().findChild(QtWidgets.QLabel, label_base)
            if label:
                label.setText(f"{label_base} ({new_unit})")

        self.unit = new_unit

    def on_helper_toggled(self):
        """
        Toggle helper spring
        """
        # store the new state
        if self.use_helper:
            self.use_helper = 0
        else:
            self.use_helper = 1

        # optionally enable/disable the other helper controls
        for w in (
            self.helper_above,
            self.helper_below,
            self.q_helper_outer_diameter,
            self.q_helper_inner_diameter,
            self.q_helper_thickness,
            self.q_helper_inner_height,
            self.q_helper_spring_id,
            self.q_helper_spring_od,
            self.q_helper_spring_free_length,
            self.q_helper_spring_rate,
            self.q_helper_spring_bind_length
        ):
            w.setEnabled(self.use_helper)

    def on_bump_toggled(self):
        """
        Toggle helper spring
        """
        # store the new state
        if self.use_bump:
            self.use_bump = 0
        else:
            self.use_bump = 1

        # optionally enable/disable the other helper controls
        for w in (
            self.radio_bump_ext,
            self.radio_bump_int,
            self.q_bump_height,
            self.q_bump_diameter,
            self.q_bump_rate,
        ):
            w.setEnabled(self.use_bump)

    def on_lower_perch_adj_toggled(self, checked):
        """
        Enable lower perch position input when adjustable perch is selected.
        """
        self.q_lower_perch_position.setEnabled(bool(checked))

    def lower_perch_sleeve_chk_toggled(self, checked):
        """
        Enable sleeve dimension inputs when using a conversion sleeve.
        """
        for w in (
            self.q_lower_perch_sleeve_height,
            self.q_lower_perch_sleeve_inner_diameter,
        ):
            w.setEnabled(bool(checked))

    def read_length(self, widget):
        """
        Ensures the 3D animation always reads the inputs in mm
        """
        val = float(widget.text())
        if self.unit == "in":
            return val * 25.4  # convert inches back to mm
        return val            # already in mm   

    def update_view(self):
        """
        Update and render the 3D visualization
        """
        # Input values
        self.spring_id = self.read_length(self.q_spring_id)
        self.spring_wire_diameter = self.read_length(self.q_spring_wire_diameter)
        self.spring_free_length = self.read_length(self.q_spring_free_length)
        self.spring_bind_length = self.read_length(self.q_spring_bind_length)
        self.spring_rate = self.read_length(self.q_spring_rate)
        self.damper_body_diameter = self.read_length(self.q_damper_body_diameter)
        self.damper_body_length = self.read_length(self.q_damper_body_length)
        self.damper_shaft_diameter = self.read_length(self.q_damper_shaft_diameter)
        self.lower_perch_position = self.read_length(self.q_lower_perch_position)
        self.damper_free_length = self.read_length(self.q_damper_free_length)
        self.damper_comp_length = self.read_length(self.q_damper_comp_length)
        self.helper_thickness = self.read_length(self.q_helper_thickness)
        self.helper_outer_diameter = self.read_length(self.q_helper_outer_diameter)
        self.helper_inner_diameter = self.read_length(self.q_helper_inner_diameter)
        self.helper_inner_height = self.read_length(self.q_helper_inner_height)
        self.helper_spring_id = self.read_length(self.q_helper_spring_id)
        self.helper_spring_od = self.read_length(self.q_helper_spring_od)
        self.helper_spring_free_length = self.read_length(self.q_helper_spring_free_length)
        self.helper_spring_rate = self.read_length(self.q_helper_spring_rate)
        self.helper_spring_bind_length = self.read_length(self.q_helper_spring_bind_length)

        self.shaft_length = self.damper_comp_length #TODO fix this simplificiation
        hole_r = (self.read_length(self.q_helper_inner_diameter) - 2 * self.helper_thickness) / 2.0 # second ring’s hole radius:

        # Clear old mesh geometry
        for item in [
            self.spring_mesh,
            self.body_mesh,
            self.shaft_mesh,
            self.upper_perch,
            self.upper_cone,
            self.helper_spring_mesh
            ]:
            if item: self.view.removeItem(item)

        # Create damper body
        cyl = make_cylinder(self.damper_body_diameter/2, self.damper_body_length, 32)
        self.body_mesh = gl.GLMeshItem(
            meshdata=cyl,
            smooth=True, 
            color=(0.4,0.4,0.4,1),
            shader='shaded',         # turn on per‐vertex lighting
            glOptions='opaque',      # so it renders solid faces
            computeNormals=True      # auto-generate normals from faces
        )
        self.body_mesh.translate(0, 0, self.damper_body_length/2) # bottom of damper body is the origin
        self.view.addItem(self.body_mesh)

        # Create damper shaft
        shaft = make_cylinder(self.damper_shaft_diameter/2, self.shaft_length, 16)
        self.shaft_mesh = gl.GLMeshItem(
            meshdata=shaft,
            smooth=True,
            color=(0.8,0.1,0.1,1),
            shader='shaded',         # turn on per‐vertex lighting
            glOptions='opaque',      # so it renders solid faces
            computeNormals=True      # auto-generate normals from faces
        )
        self.shaft_mesh.translate(0, 0, (self.shaft_length/2 + (self.damper_free_length - self.damper_comp_length)))
        self.view.addItem(self.shaft_mesh)

        # Create main spring helix
        self.coils = calculate_active_coils(50, self.spring_wire_diameter, self.spring_id)
        theta  = np.linspace(0, 2*np.pi*self.coils, 200)
        self.spring_x = ((self.spring_id + self.spring_wire_diameter)/2) * np.cos(theta)
        self.spring_y = ((self.spring_id + self.spring_wire_diameter)/2) * np.sin(theta)
        self.main_theta = theta

        # Create main spring geometry
        self.spring_bottom_position = self.damper_body_length + self.lower_perch_position + self.spring_wire_diameter / 2 # Z coordinate where the bottom spring wire's center sits
        self.spring_upper_position = self.spring_bottom_position + self.spring_free_length - self.spring_wire_diameter # Z coordinate where the top spring wire's center sits
        pts = np.vstack((self.spring_x, self.spring_y, np.linspace(self.spring_bottom_position, self.spring_upper_position, self.main_theta.size))).T
        wire = make_spring_wire(pts, self.spring_wire_diameter/2)
        self.spring_mesh = gl.GLMeshItem(
            meshdata=wire,
            smooth=True,
            color=(0.1,0.1,0.8,1),
            shader='shaded',         # turn on per‐vertex lighting
            glOptions='opaque',      # so it renders solid faces
            computeNormals=True      # auto-generate normals from faces
            )
        self.view.addItem(self.spring_mesh)

        # Create helper spring helix
        self.helper_wire_width = (self.helper_outer_diameter - self.helper_inner_diameter) / 2
        self.helper_coils, self.helper_wire_height = calculate_active_coils_rectangular(
            spring_rate=self.helper_spring_rate,
            inner_diameter=self.helper_inner_diameter,
            outer_diameter=self.helper_outer_diameter,
            shear_modulus=80e3,
            wire_width=self.helper_wire_width,
            solid_height=self.helper_spring_bind_length
        )
        self.helper_spring_lower_position = self.spring_upper_position + self.spring_wire_diameter / 2 + self.helper_thickness + self.helper_wire_height / 2 # Z coordinate where the bottom spring wire's center sits
        self.helper_spring_upper_position = self.helper_spring_lower_position + self.helper_spring_free_length - self.helper_wire_height # Z coordinate where the top spring wire's center sits
        theta  = np.linspace(0, 2 * np.pi * self.helper_coils, 200)
        r = (self.helper_inner_diameter + self.helper_wire_width) / 2
        self.helper_spring_x = r * np.cos(theta)
        self.helper_spring_y = r * np.sin(theta)
        self.helper_theta = theta

        # Create helper spring geometry
        pts = np.vstack((self.helper_spring_x, self.helper_spring_y, np.linspace(self.helper_spring_lower_position, self.helper_spring_upper_position, self.helper_theta.size))).T
        wire = make_rectangular_spring_wire(pts, self.helper_wire_width, self.helper_wire_height)
        self.helper_spring_mesh = gl.GLMeshItem(
            meshdata=wire,
            smooth=True,
            color=(0.1,0.1,0.8,1),
            shader='shaded',         # turn on per‐vertex lighting
            glOptions='opaque',      # so it renders solid faces
            computeNormals=True      # auto-generate normals from faces
            )
        self.view.addItem(self.helper_spring_mesh)

        # Upper spring perch
        perch_clearance  = 2.0       # mm beyond spring OD
        cyl_thickness    = 5.0       # cylinder height
        cone_height      = 10.0      # cone height
        plate_dia        = 87

        cyl_mesh = make_cylinder(plate_dia/2.0, cyl_thickness, sectors=32)
        self.upper_perch = gl.GLMeshItem(
            meshdata=cyl_mesh, smooth=True,
            color=(1.0, 0.5, 0.0, 1.0),
            shader='shaded', glOptions='opaque', computeNormals=True
        )
        # center its bottom on spring_top_z:
        cyl_center_z = self.damper_free_length + cyl_thickness/2.0
        self.upper_perch.translate(0, 0, cyl_center_z)
        self.view.addItem(self.upper_perch)

        # Build cone for upper perch
        # Build base ring
        n_segs = 32
        angles = np.linspace(0, 2*np.pi, n_segs, endpoint=False)
        base_pts = np.vstack([
            plate_dia/2.0*np.cos(angles),
            plate_dia/2.0*np.sin(angles),
            np.full_like(angles, self.damper_free_length + cyl_thickness)
        ]).T
        # tip vertex
        tip = np.array([0, 0, self.damper_free_length + cyl_thickness + cone_height])

        # assemble verts & faces
        verts = np.vstack([base_pts, tip])
        faces = []
        tip_idx = len(verts) - 1
        for i in range(n_segs):
            a = i
            b = (i+1) % n_segs
            # triangle (a, b, tip)
            faces.append([a, b, tip_idx])

        cone_mesh = gl.MeshData(vertexes=verts, faces=np.array(faces))
        self.upper_cone = gl.GLMeshItem(
            meshdata=cone_mesh, smooth=True,
            color=(1.0, 0.5, 0.0, 1.0),
            shader='shaded', glOptions='opaque', computeNormals=True
        )
        self.view.addItem(self.upper_cone)

        # Lower spring perch
        perch_clearance  = 2.0       # mm beyond spring OD
        cyl_thickness    = 10.0       # cylinder height
        cone_height      = 10.0      # cone height
        plate_dia        = 87

        # remove old perch if exists
        if hasattr(self, 'lower_perch'):
            self.view.removeItem(self.lower_perch)

        cyl_mesh = make_cylinder(plate_dia/2.0, cyl_thickness, sectors=32)
        self.lower_perch = gl.GLMeshItem(
            meshdata=cyl_mesh, smooth=True,
            color=(0.0, 0.7, 1.0, 1.0),
            shader='shaded', glOptions='opaque', computeNormals=True
        )
        # center its top on spring_top_z:
        lower_perch_z = self.damper_body_length - cyl_thickness/2.0 + self.lower_perch_position
        self.lower_perch.translate(0, 0, lower_perch_z)
        self.view.addItem(self.lower_perch)

        # helper spring perch
        # --- remove old helper perch if present ---
        if hasattr(self, 'helper_perch'):
            self.view.removeItem(self.helper_perch)

        # --- build the two annular meshes ---
        md1 = make_annular_cylinder(self.helper_outer_diameter / 2,   self.helper_inner_diameter / 2, self.helper_thickness, sectors=64)
        md2 = make_annular_cylinder(self.helper_inner_diameter / 2, hole_r, self.helper_inner_height, sectors=64)

        # --- merge them into one mesh ---
        v1, f1 = md1.vertexes(), md1.faces()
        v2, f2 = md2.vertexes(), md2.faces()
        verts = np.vstack([v1, v2])
        faces = np.vstack([f1, f2 + len(v1)])
        helper_mesh = gl.MeshData(vertexes=verts, faces=faces)

        # --- create the GL item ---
        self.helper_perch = gl.GLMeshItem(
            meshdata=helper_mesh, smooth=True,
            color=(1.0, 0.0, 0.8, 1.0), shader='shaded',
            glOptions='opaque', computeNormals=True
        )

        self.helper_perch.translate(0, 0, (self.damper_body_length + self.lower_perch_position + self.spring_free_length + self.helper_thickness/2))
        self.view.addItem(self.helper_perch)


        # travel info
        self.animate(self.slider.value())

    def animate(self, t):
        """
        t = 0 to 100 slider: moves spring + shaft
        """
        
        f = t / 100

        # Calculate minimum allowable shaft position
        min_shaft_position = max(self.damper_comp_length, (self.spring_bottom_position - self.spring_wire_diameter / 2 + self.spring_bind_length + self.helper_spring_bind_length + self.helper_thickness))

        # Compute the damper length given the slider position
        self.shaft_upper_position   = self.damper_free_length - (self.damper_free_length - min_shaft_position) * f

        # Calculate the available room between the perches
        available_length = self.shaft_upper_position - (self.spring_bottom_position - self.spring_wire_diameter / 2) - self.helper_thickness

        # Calculate the spring lengths and total force
        spring_length, helper_spring_length, spring_force = split_strut_length_to_springs(
            self.spring_rate,
            self.helper_spring_rate,
            available_length,
            self.spring_bind_length,
            self.helper_spring_bind_length,
            self.spring_free_length,
            self.helper_spring_free_length
        )

        # Calculate the spring wire positions and the helper perch position
        self.spring_upper_position = self.spring_bottom_position + (spring_length - self.spring_wire_diameter)
        self.helper_perch_position = self.spring_upper_position + self.spring_wire_diameter / 2 + self.helper_thickness / 2
        self.helper_spring_lower_position = self.helper_perch_position + self.helper_thickness / 2 + self.helper_wire_height / 2
        self.helper_spring_upper_position = self.helper_spring_lower_position + (helper_spring_length - self.helper_wire_height)

        # Regenerate the main spring helix
        zs = np.linspace(self.spring_bottom_position, self.spring_upper_position, self.main_theta.size)
        pts = np.vstack((self.spring_x, self.spring_y, zs)).T
        new_wire = make_spring_wire(pts, self.spring_wire_diameter/2)
        self.spring_mesh.setMeshData(meshdata=new_wire)

        # Regenerate the helper spring helix
        zs = np.linspace(self.helper_spring_lower_position, self.helper_spring_upper_position, self.helper_theta.size)
        pts = np.vstack((self.helper_spring_x, self.helper_spring_y, zs)).T
        new_wire = make_rectangular_spring_wire(pts, self.helper_wire_width, self.helper_wire_height)
        self.helper_spring_mesh.setMeshData(meshdata=new_wire)

        # Move the damper shaft
        shaft_center = self.shaft_upper_position - self.shaft_length/2
        self.shaft_mesh.resetTransform()
        self.shaft_mesh.translate(0, 0, shaft_center)

        # Move upper spring perch
        self.upper_perch.resetTransform()
        self.upper_perch.translate(0, 0, self.shaft_upper_position + 2.5) # TODO: add inputs for perch geometries
        self.upper_cone.resetTransform()
        self.upper_cone.translate(0, 0, (self.shaft_upper_position - self.damper_free_length))

        # Move helper perch
        self.helper_perch.resetTransform()
        self.helper_perch.translate(0, 0, self.helper_perch_position)

        # Update overlay text
        self.info_label.setText(f"Coilover length: {self.shaft_upper_position:.1f} mm\n" + 
                                f"Availible length: {available_length:.1f} mm\n" +
                                f"Main Spring length: {spring_length:.1f} mm\n" +
                                f"Helper Spring length: {helper_spring_length:.1f} mm\n" + 
                                f"Spring Force: {spring_force:.1f} N\n")
        self.info_label.adjustSize()

        # get view size
        w = self.view.width()
        h = self.view.height()
        lbl_w = self.help_label.width()
        lbl_h = self.help_label.height()
        # center horizontally, place 10px above bottom
        self.help_label.move((w - lbl_w)//2, h - lbl_h - 10)
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = CoiloverDesigner()
    win.show()
    sys.exit(app.exec_())
