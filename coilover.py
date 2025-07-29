import sys
import numpy as np

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QVector3D
import pyqtgraph as pg
import pyqtgraph.opengl as gl

class CoiloverDesigner(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coilover Tool")
        self.resize(1000, 600)

        # === Left panel: parameter inputs ===
        form = QtWidgets.QFormLayout()

        # text field variables
        self.q_spring_id                    = QtWidgets.QLineEdit("60")   # mm
        self.q_spring_wire_diameter         = QtWidgets.QLineEdit("10")   # mm
        self.q_spring_free_length           = QtWidgets.QLineEdit("200")  # mm
        self.q_spring_rate                  = QtWidgets.QLineEdit("100")  # N/mm
        self.q_spring_bind_length           = QtWidgets.QLineEdit("50")   # mm

        self.q_damper_free_length           = QtWidgets.QLineEdit("400")  # mm
        self.q_damper_comp_length           = QtWidgets.QLineEdit("250")  # mm
        self.q_damper_body_length           = QtWidgets.QLineEdit("200")  # mm
        self.q_damper_body_diameter         = QtWidgets.QLineEdit("50")   # mm
        self.q_damper_shaft_diameter        = QtWidgets.QLineEdit("20")   # mm
        self.q_body_threaded_length         = QtWidgets.QLineEdit("100")  # mm

        self.use_helper = 0
        self.q_helper_outer_diameter        = QtWidgets.QLineEdit("85")
        self.q_helper_inner_diameter        = QtWidgets.QLineEdit("64")
        self.q_helper_thickness             = QtWidgets.QLineEdit("2")
        self.q_helper_inner_height          = QtWidgets.QLineEdit("10")
        self.q_helper_spring_id             = QtWidgets.QLineEdit("57.15") # mm
        self.q_helper_spring_od             = QtWidgets.QLineEdit("73.91") # mm
        self.q_helper_spring_free_length    = QtWidgets.QLineEdit("101.6") # mm
        self.q_helper_spring_rate           = QtWidgets.QLineEdit("2.63")  # N/mm
        self.q_helper_spring_bind_length    = QtWidgets.QLineEdit("11.18") # mm

        self.use_bump = 0
        self.q_bump_height                  = QtWidgets.QLineEdit("25")
        self.q_bump_diameter                = QtWidgets.QLineEdit("50")
        self.q_bump_rate                    = QtWidgets.QLineEdit("50")

        self.q_lower_perch_position         = QtWidgets.QLineEdit("10")   # mm

        self.unit = "mm"

        # Settings group
        settings_group  = QtWidgets.QGroupBox("Settings")
        settings_layout = QtWidgets.QHBoxLayout()

        self.radio_mm = QtWidgets.QRadioButton("mm")
        self.radio_in = QtWidgets.QRadioButton("in")
        self.radio_mm.setChecked(True)           # default = millimeters
        self.radio_mm.toggled.connect(self.on_unit_changed)

        settings_layout.addWidget(self.radio_mm)
        settings_layout.addWidget(self.radio_in)
        settings_group.setLayout(settings_layout)

        # Spring group
        spring_group   = QtWidgets.QGroupBox("Spring")
        spring_layout  = QtWidgets.QFormLayout()

        lbl = QtWidgets.QLabel("Inner diameter (mm):")
        lbl.setObjectName("Inner diameter")
        spring_layout.addRow(lbl,   self.q_spring_id)

        lbl = QtWidgets.QLabel("Wire diameter (mm):")
        lbl.setObjectName("Wire diameter")
        spring_layout.addRow(lbl,   self.q_spring_wire_diameter)

        lbl = QtWidgets.QLabel("Spring free length (mm):")
        lbl.setObjectName("Spring free length")
        spring_layout.addRow(lbl,      self.q_spring_free_length)

        lbl = QtWidgets.QLabel("Spring Rate (N/mm):")
        lbl.setObjectName("Spring Rate")
        spring_layout.addRow(lbl,           self.q_spring_rate)

        lbl = QtWidgets.QLabel("Length at bind (mm):")
        lbl.setObjectName("Length at bind")
        spring_layout.addRow(lbl,   self.q_spring_bind_length)

        spring_group.setLayout(spring_layout)

        # Damper group
        damper_group  = QtWidgets.QGroupBox("Damper")
        damper_layout = QtWidgets.QFormLayout()

        lbl = QtWidgets.QLabel("Damper free length (mm):")
        lbl.setObjectName("Damper free length")
        damper_layout.addRow(lbl,           self.q_damper_free_length)

        lbl = QtWidgets.QLabel("Compressed length (mm):")
        lbl.setObjectName("Compressed length")
        damper_layout.addRow(lbl,     self.q_damper_comp_length)

        lbl = QtWidgets.QLabel("Body length (mm):")
        lbl.setObjectName("Body length")
        damper_layout.addRow(lbl,           self.q_damper_body_length)

        lbl = QtWidgets.QLabel("Body diameter (mm):")
        lbl.setObjectName("Body diameter")
        damper_layout.addRow(lbl,         self.q_damper_body_diameter)

        lbl = QtWidgets.QLabel("Shaft diameter (mm):")
        lbl.setObjectName("Shaft diameter")
        damper_layout.addRow(lbl,        self.q_damper_shaft_diameter)

        lbl = QtWidgets.QLabel("Body threaded length (mm):")
        lbl.setObjectName("Body threaded length")
        damper_layout.addRow(lbl, self.q_body_threaded_length)

        damper_group.setLayout(damper_layout)

        # Helper spring group
        helper_group  = QtWidgets.QGroupBox("Helper spring")
        helper_layout = QtWidgets.QFormLayout()

        self.helper_chk = QtWidgets.QCheckBox("Add helper spring")
        helper_layout.addRow(self.helper_chk)
        self.helper_chk.toggled.connect(self.on_helper_toggled)

        self.helper_above = QtWidgets.QRadioButton("Above main spring")
        self.helper_below = QtWidgets.QRadioButton("Below main spring")
        self.helper_above.setChecked(True)
        # self.helper_above.toggled.connect(self.helper_change) #TODO

        rb_container = QtWidgets.QWidget()
        rb_layout    = QtWidgets.QHBoxLayout(rb_container)
        rb_layout.setContentsMargins(0,0,0,0)
        rb_layout.addWidget(self.helper_above)
        rb_layout.addWidget(self.helper_below)
        helper_layout.addRow(rb_container)   # place the two buttons in one row

        # Helper perch dimensions
        lbl = QtWidgets.QLabel("Helper perch outer diameter (mm):")
        lbl.setObjectName("Helper perch outer diameter")
        helper_layout.addRow(lbl, self.q_helper_outer_diameter)

        lbl = QtWidgets.QLabel("Helper perch inner diameter (mm):")
        lbl.setObjectName("Helper perch inner diameter")
        helper_layout.addRow(lbl, self.q_helper_inner_diameter)

        lbl = QtWidgets.QLabel("Helper perch thickness (mm):")
        lbl.setObjectName("Helper perch thickness")
        helper_layout.addRow(lbl, self.q_helper_thickness)

        lbl = QtWidgets.QLabel("Helper perch inner height (mm):")
        lbl.setObjectName("Helper perch inner height")
        helper_layout.addRow(lbl, self.q_helper_inner_height)

        # Helper spring dimensions

        lbl = QtWidgets.QLabel("Helper spring inner diameter (mm):")
        lbl.setObjectName("Helper spring inner diameter")
        helper_layout.addRow(lbl, self.q_helper_spring_id)

        lbl = QtWidgets.QLabel("Helper spring outer diameter (mm):")
        lbl.setObjectName("Helper spring inner diameter")
        helper_layout.addRow(lbl, self.q_helper_spring_od)

        lbl = QtWidgets.QLabel("Helper spring free length (mm):")
        lbl.setObjectName("Helper spring free length")
        helper_layout.addRow(lbl, self.q_helper_spring_free_length)

        lbl = QtWidgets.QLabel("Helper spring rate (N/mm):")
        lbl.setObjectName("Helper spring rate")
        helper_layout.addRow(lbl, self.q_helper_spring_rate)

        lbl = QtWidgets.QLabel("Length at bind (mm):")
        lbl.setObjectName("Length at bind")
        helper_layout.addRow(lbl, self.q_helper_spring_bind_length)

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
            w.setEnabled(self.use_bump)

        helper_group.setLayout(helper_layout)

        # Bump stop group
        bump_group  = QtWidgets.QGroupBox("Bump Stop")
        bump_layout = QtWidgets.QFormLayout()

        self.bump_chk = QtWidgets.QCheckBox("Add bump stop")
        bump_layout.addRow(self.bump_chk)
        self.bump_chk.toggled.connect(self.on_bump_toggled)

        self.radio_bump_ext = QtWidgets.QRadioButton("External")
        self.radio_bump_int = QtWidgets.QRadioButton("Internal")
        self.radio_bump_ext.setChecked(True)
        # self.radio_bump_ext.toggled.connect(self.bump_change) #TODO

        bump_rb_container = QtWidgets.QWidget()
        bump_rb_layout    = QtWidgets.QHBoxLayout(bump_rb_container)
        bump_rb_layout.setContentsMargins(0,0,0,0)
        bump_rb_layout.addWidget(self.radio_bump_ext)
        bump_rb_layout.addWidget(self.radio_bump_int)
        bump_layout.addRow(bump_rb_container)   # place the two buttons in one row

        lbl = QtWidgets.QLabel("Bump stop height (mm):")
        lbl.setObjectName("Bump stop height")
        bump_layout.addRow(lbl, self.q_bump_height)

        lbl = QtWidgets.QLabel("Bump stop outer diameter (mm):")
        lbl.setObjectName("Bump stop outer diameter")
        bump_layout.addRow(lbl, self.q_bump_diameter)

        lbl = QtWidgets.QLabel("Bump stop spring rate (mm):")
        lbl.setObjectName("Bump stop spring rate")
        bump_layout.addRow(lbl, self.q_bump_rate)

        for w in (
            self.radio_bump_ext,
            self.radio_bump_int,
            self.q_bump_height,
            self.q_bump_diameter,
            self.q_bump_rate,
        ):
            w.setEnabled(self.use_bump)

        bump_group.setLayout(bump_layout)

        # Setup group
        setup_group  = QtWidgets.QGroupBox("Setup")
        setup_layout = QtWidgets.QFormLayout()

        self.flip_damper_chk = QtWidgets.QCheckBox("Flip damper orientation")
        setup_layout.addRow(self.flip_damper_chk)

        lbl = QtWidgets.QLabel("Spring perch starting point (mm):")
        lbl.setObjectName("Spring perch starting point")
        setup_layout.addRow(lbl, self.q_lower_perch_position)

        setup_group.setLayout(setup_layout)

        # Assemble left‐side layout
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(settings_group)
        left_layout.addWidget(spring_group)
        left_layout.addWidget(damper_group)
        left_layout.addWidget(helper_group)
        left_layout.addWidget(bump_group)
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

    def read_length(self, widget):
        """
        Ensures the 3D animation always reads the inputs in mm
        """
        val = float(widget.text())
        if self.unit == "in":
            return val * 25.4  # convert inches back to mm
        return val            # already in mm

    def make_annular_cylinder(self, outer_r, inner_r, height, sectors=32):
        """
        Returns a MeshData for a flat ring (outer radius outer_r, inner radius inner_r)
        of thickness `height` centered on z=0.
        """
        # angles for your circle
        theta = np.linspace(0, 2*np.pi, sectors, endpoint=False)
        cos, sin = np.cos(theta), np.sin(theta)

        # top & bottom rings: outer & inner
        top_outer    = np.column_stack([outer_r*cos,        outer_r*sin,        np.full(sectors,  height/2)])
        bot_outer    = np.column_stack([outer_r*cos,        outer_r*sin,        np.full(sectors, -height/2)])
        top_inner    = np.column_stack([inner_r*cos,        inner_r*sin,        np.full(sectors,  height/2)])
        bot_inner    = np.column_stack([inner_r*cos,        inner_r*sin,        np.full(sectors, -height/2)])

        verts = np.vstack([top_outer, bot_outer, top_inner, bot_inner])
        faces = []

        # helper to index sections
        O  = 0
        B  = sectors
        I  = 2*sectors
        BI = 3*sectors

        # outer wall
        for i in range(sectors):
            a = O + i
            b = O + (i+1)%sectors
            c = B + i
            d = B + (i+1)%sectors
            faces += [[a, c, b], [b, c, d]]

        # inner wall (flip winding so normals point inward)
        for i in range(sectors):
            a = I + i
            b = I + (i+1)%sectors
            c = BI + i
            d = BI + (i+1)%sectors
            faces += [[c, a, b], [b, d, c]]

        # top face (between outer & inner)
        for i in range(sectors):
            a = O + i
            b = O + (i+1)%sectors
            c = I + i
            d = I + (i+1)%sectors
            faces += [[a, b, c], [b, d, c]]

        # bottom face
        for i in range(sectors):
            a = B + i
            b = B + (i+1)%sectors
            c = BI + i
            d = BI + (i+1)%sectors
            faces += [[b, a, c], [a, d, c]]

        return gl.MeshData(vertexes=verts, faces=np.array(faces))


    def make_spring_wire(self, path_pts, wire_radius, n_sides=8):
        """
        Sweeps along the spring helix to create the spring geometry
        path_pts: (N,3) array of helix points
        wire_radius: radius of spring wire in same units as path_pts
        returns: MeshData for a tube
        """
        N = len(path_pts)
        # Compute tangents
        tangents = np.diff(path_pts, axis=0)
        tangents = np.vstack([tangents, tangents[-1]])          # last tangent = previous
        tangents /= np.linalg.norm(tangents, axis=1)[:,None]
        
        # Pick an arbitrary initial normal
        #    (e.g. project world‐Z onto plane orthogonal to tangent[0])
        #    then Gram–Schmidt to get a stable frame
        normals = np.zeros_like(path_pts)
        binorms = np.zeros_like(path_pts)
        # initial:
        arbitrary = np.array([0,0,1.0])
        normals[0] = np.cross(tangents[0], arbitrary)
        normals[0] = normals[0] / np.linalg.norm(normals[0])
        binorms[0] = np.cross(tangents[0], normals[0])
        
        # Propagate via parallel transport (simple approach)
        for i in range(1, N):
            # make sure normals stay orthogonal to new tangent:
            v = normals[i-1] - tangents[i] * np.dot(tangents[i], normals[i-1])
            normals[i] = v / np.linalg.norm(v)
            binorms[i] = np.cross(tangents[i], normals[i])
        
        # Generate circle in local frames
        theta = np.linspace(0, 2*np.pi, n_sides, endpoint=False)
        circle = np.vstack([np.cos(theta), np.sin(theta)]) * wire_radius  # (2, S)
        
        verts = []
        faces = []
        for i, p in enumerate(path_pts):
            # build ring i
            for j in range(n_sides):
                offset = normals[i]*circle[0,j] + binorms[i]*circle[1,j]
                verts.append(p + offset)
        verts = np.array(verts)  # (N * S, 3)
        
        # Build faces by connecting ring i to i+1
        for i in range(N-1):
            for j in range(n_sides):
                a = i*n_sides + j
                b = i*n_sides + (j+1)%n_sides
                c = (i+1)*n_sides + j
                d = (i+1)*n_sides + (j+1)%n_sides
                # two triangles (a, c, b) and (b, c, d)
                faces.append([a, c, b])
                faces.append([b, c, d])
        
        mesh = gl.MeshData(vertexes=verts, faces=np.array(faces))
        return mesh

    def calculate_active_coils(self, spring_rate, 
                            wire_diameter, 
                            inner_diameter, 
                            shear_modulus=80000):
        """
        Calculate the number of active coils needed for a helical compression spring.

        Parameters
        ----------
        spring_rate : float
            Desired spring rate K in N/mm.
        wire_diameter : float
            Wire diameter d in mm.
        inner_diameter : float
            Inner diameter ID of the spring in mm.
        shear_modulus : float, optional
            Shear modulus G in N/mm² (default=80000 N/mm² for steel).

        Returns
        -------
        float
            Required number of active coils (n).
        """
        # mean coil diameter
        D = inner_diameter + wire_diameter

        # torsion‐spring formula solved for n
        n_active = (shear_modulus * wire_diameter**4) / (8 * spring_rate * D**3)
        return n_active    

    def update_view(self):
        """
        Update and render the 3D visualization
        """
        # Input values
        self.spring_id      = self.read_length(self.q_spring_id)
        self.spring_wire_diameter   = self.read_length(self.q_spring_wire_diameter)
        self.spring_free_length      = self.read_length(self.q_spring_free_length)
        self.spring_bind_length   = self.read_length(self.q_spring_bind_length)
        self.damper_body_diameter   = self.read_length(self.q_damper_body_diameter)
        self.damper_body_length   = self.read_length(self.q_damper_body_length)
        self.damper_shaft_diameter  = self.read_length(self.q_damper_shaft_diameter)
        self.lower_perch_position   = self.read_length(self.q_lower_perch_position)
        self.damper_free_length   = self.read_length(self.q_damper_free_length)
        self.damper_comp_length  = self.read_length(self.q_damper_comp_length)
        self.helper_thickness   = self.read_length(self.q_helper_thickness)
        self.helper_outer_diameter   = self.read_length(self.q_helper_outer_diameter)
        self.helper_inner_diameter  = self.read_length(self.q_helper_inner_diameter)
        self.helper_inner_height   = self.read_length(self.q_helper_inner_height)

        # Calculate values
        self.spring_bottom_position = self.damper_body_length + self.lower_perch_position + self.spring_wire_diameter/2 # Z coordinate where spring’s bottom sits
        self.spring_upper_position = -min(self.spring_free_length - self.spring_bind_length, self.spring_free_length) # Z coordinate where spring’s top sits
        self.shaft_length = self.damper_comp_length #TODO fix this simplificiation
        hole_r = (self.read_length(self.q_helper_inner_diameter) - 2 * self.helper_thickness) / 2.0 # second ring’s hole radius:

        # Clear old mesh geometry
        for item in [self.spring_mesh, self.body_mesh, self.shaft_mesh, self.upper_perch, self.upper_cone]:
            if item: self.view.removeItem(item)

        # Create damper body
        cyl = self.make_cylinder(self.damper_body_diameter/2, self.damper_body_length, 32)
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
        shaft = self.make_cylinder(self.damper_shaft_diameter/2, self.shaft_length, 16)
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
        self.coils = self.calculate_active_coils(50, self.spring_wire_diameter, self.spring_id)
        theta  = np.linspace(0, 2*np.pi*self.coils, 200)
        self.spring_x = (self.spring_id/2) * np.cos(theta)
        self.spring_y = (self.spring_id/2) * np.sin(theta)
        self.theta    = theta

        # Create main spring geometry
        z0 = self.spring_bottom_position
        z1 = z0 + self.spring_free_length
        pts = np.vstack((self.spring_x, self.spring_y, np.linspace(z0, z1, theta.size))).T
        wire = self.make_spring_wire(pts, self.spring_wire_diameter/2)
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
        self.helper_coils = self.calculate_active_coils(50, self.spring_wire_diameter, self.spring_id) #TODO calculate for flat wire cross section
        theta  = np.linspace(0, 2*np.pi*self.coils, 200)
        self.spring_x = (self.spring_id/2) * np.cos(theta)
        self.spring_y = (self.spring_id/2) * np.sin(theta)
        self.theta    = theta

        # Create helper spring geometry
        z0 = self.spring_bottom_position
        z1 = z0 + self.spring_free_length
        pts = np.vstack((self.spring_x, self.spring_y, np.linspace(z0, z1, theta.size))).T
        wire = self.make_spring_wire(pts, self.spring_wire_diameter/2)
        self.spring_mesh = gl.GLMeshItem(
            meshdata=wire,
            smooth=True,
            color=(0.1,0.1,0.8,1),
            shader='shaded',         # turn on per‐vertex lighting
            glOptions='opaque',      # so it renders solid faces
            computeNormals=True      # auto-generate normals from faces
            )
        self.view.addItem(self.spring_mesh)

        # Upper spring perch
        perch_clearance  = 2.0       # mm beyond spring OD
        cyl_thickness    = 5.0       # cylinder height
        cone_height      = 10.0      # cone height
        plate_dia        = self.spring_id + perch_clearance

        cyl_mesh = self.make_cylinder(plate_dia/2.0, cyl_thickness, sectors=32)
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
        cyl_thickness    = 5.0       # cylinder height
        cone_height      = 10.0      # cone height
        plate_dia        = self.spring_id + perch_clearance

        # remove old perch if exists
        if hasattr(self, 'lower_perch'):
            self.view.removeItem(self.lower_perch)

        cyl_mesh = self.make_cylinder(plate_dia/2.0, cyl_thickness, sectors=32)
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
        md1 = self.make_annular_cylinder(self.helper_outer_diameter / 2,   self.helper_inner_diameter / 2, self.helper_thickness, sectors=64)
        md2 = self.make_annular_cylinder(self.helper_inner_diameter / 2, hole_r, self.helper_inner_height, sectors=64)

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
        t = 0..100 slider: moves spring + shaft
        """
        f = t / 100

        # Compute current spring length
        self.shaft_upper_position   = self.damper_free_length - (self.damper_free_length - self.damper_comp_length) * f

        # Check if spring is loose
        if self.shaft_upper_position - (self.spring_wire_diameter / 2) < (self.spring_bottom_position + self.spring_free_length):
            self.spring_upper_position  = self.shaft_upper_position - (self.spring_wire_diameter / 2)
        else:
            self.spring_upper_position = self.spring_bottom_position + self.spring_free_length
        spring_length = self.spring_upper_position - self.spring_bottom_position

        # Check if in coil bind
        if spring_length < self.spring_bind_length:
            spring_length = self.spring_bind_length
            self.spring_upper_position = self.spring_bottom_position + self.spring_bind_length
            self.shaft_upper_position = self.spring_upper_position + (self.spring_wire_diameter / 2)

        # Regenerate the helix points & update the line
        zs = np.linspace(self.spring_bottom_position, self.spring_upper_position, self.theta.size)
        pts = np.vstack((self.spring_x, self.spring_y, zs)).T
        new_wire = self.make_spring_wire(pts, self.spring_wire_diameter/2)
        self.spring_mesh.setMeshData(meshdata=new_wire)

        # Move the shaft so its bottom rests on the spring top
        shaft_center = self.shaft_upper_position - self.shaft_length/2
        self.shaft_mesh.resetTransform()
        self.shaft_mesh.translate(0, 0, shaft_center)

        # Move upper spring perch
        self.upper_perch.resetTransform()
        self.upper_perch.translate(0, 0, self.shaft_upper_position + 2.5)
        self.upper_cone.resetTransform()
        self.upper_cone.translate(0, 0, (self.shaft_upper_position - self.damper_free_length))

        # Move helper perch
        self.helper_perch.resetTransform()
        self.helper_perch.translate(0, 0, (self.spring_upper_position + (self.spring_wire_diameter / 2) + (self.helper_thickness / 2)))


        # Update overlay text
        self.info_label.setText(f"Coilover length: {self.shaft_upper_position:.1f} mm\nSpring length: {spring_length:.1f} mm")
        self.info_label.adjustSize()

        # get view size
        w = self.view.width()
        h = self.view.height()
        lbl_w = self.help_label.width()
        lbl_h = self.help_label.height()
        # center horizontally, place 10px above bottom
        self.help_label.move((w - lbl_w)//2, h - lbl_h - 10)

    @staticmethod
    def make_cylinder(radius, length, sectors):
        """Returns a MeshData cylinder aligned along z."""
        theta = np.linspace(0, 2*np.pi, sectors)
        xs, ys = np.cos(theta)*radius, np.sin(theta)*radius
        # top and bottom circles
        top    = np.vstack([xs, ys, np.full_like(xs, length/2)]).T
        bottom = np.vstack([xs, ys, np.full_like(xs, -length/2)]).T
        faces = []
        verts = np.vstack([top, bottom])
        # side faces
        for i in range(sectors-1):
            faces.append([i, i+1, sectors + i])
            faces.append([i+1, sectors+1 + i, sectors + i])
        # close the loop
        faces.append([sectors-1, 0, 2*sectors-1])
        faces.append([0, sectors, 2*sectors-1])
        return gl.MeshData(vertexes=verts, faces=np.array(faces))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = CoiloverDesigner()
    win.show()
    sys.exit(app.exec_())