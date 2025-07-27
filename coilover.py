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
        self.spring_id              = QtWidgets.QLineEdit("60")   # mm
        self.spring_wire_dia        = QtWidgets.QLineEdit("10")   # mm
        self.spring_free            = QtWidgets.QLineEdit("200")  # mm
        self.spring_rate            = QtWidgets.QLineEdit("100")  # N/mm
        self.spring_bind            = QtWidgets.QLineEdit("50")   # mm

        self.damper_free            = QtWidgets.QLineEdit("400")  # mm
        self.damper_compr           = QtWidgets.QLineEdit("250")  # mm
        self.damper_body_len        = QtWidgets.QLineEdit("200")  # mm
        self.damper_body_dia        = QtWidgets.QLineEdit("50")   # mm
        self.damper_shaft_dia       = QtWidgets.QLineEdit("20")   # mm
        self.body_threaded_length   = QtWidgets.QLineEdit("100")   # mm

        self.use_helper = 0
        self.helper_outer_diam      = QtWidgets.QLineEdit("85")
        self.helper_inner_diam      = QtWidgets.QLineEdit("64")
        self.helper_thickness       = QtWidgets.QLineEdit("2")
        self.helper_inner_height    = QtWidgets.QLineEdit("10")
        self.helper_spring_id       = QtWidgets.QLineEdit("57.15")   # mm
        self.helper_spring_od       = QtWidgets.QLineEdit("73.91")   # mm
        self.helper_spring_free     = QtWidgets.QLineEdit("101.6")  # mm
        self.helper_spring_rate     = QtWidgets.QLineEdit("2.63")  # N/mm
        self.helper_spring_bind     = QtWidgets.QLineEdit("11.18")   # mm

        self.use_bump = 0
        self.bump_height            = QtWidgets.QLineEdit("25")
        self.bump_diam              = QtWidgets.QLineEdit("50")
        self.bump_rate              = QtWidgets.QLineEdit("50")

        self.perch_input            = QtWidgets.QLineEdit("10")   # mm

        self.shaft_length     = float(self.damper_compr.text())
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
        spring_layout.addRow(lbl,   self.spring_id)

        lbl = QtWidgets.QLabel("Wire diameter (mm):")
        lbl.setObjectName("Wire diameter")
        spring_layout.addRow(lbl,   self.spring_wire_dia)

        lbl = QtWidgets.QLabel("Spring free length (mm):")
        lbl.setObjectName("Spring free length")
        spring_layout.addRow(lbl,      self.spring_free)

        lbl = QtWidgets.QLabel("Spring Rate (N/mm):")
        lbl.setObjectName("Spring Rate")
        spring_layout.addRow(lbl,           self.spring_rate)

        lbl = QtWidgets.QLabel("Length at bind (mm):")
        lbl.setObjectName("Length at bind")
        spring_layout.addRow(lbl,   self.spring_bind)

        spring_group.setLayout(spring_layout)

        # Damper group
        damper_group  = QtWidgets.QGroupBox("Damper")
        damper_layout = QtWidgets.QFormLayout()

        lbl = QtWidgets.QLabel("Damper free length (mm):")
        lbl.setObjectName("Damper free length")
        damper_layout.addRow(lbl,           self.damper_free)

        lbl = QtWidgets.QLabel("Compressed length (mm):")
        lbl.setObjectName("Compressed length")
        damper_layout.addRow(lbl,     self.damper_compr)

        lbl = QtWidgets.QLabel("Body length (mm):")
        lbl.setObjectName("Body length")
        damper_layout.addRow(lbl,           self.damper_body_len)

        lbl = QtWidgets.QLabel("Body diameter (mm):")
        lbl.setObjectName("Body diameter")
        damper_layout.addRow(lbl,         self.damper_body_dia)

        lbl = QtWidgets.QLabel("Shaft diameter (mm):")
        lbl.setObjectName("Shaft diameter")
        damper_layout.addRow(lbl,        self.damper_shaft_dia)

        lbl = QtWidgets.QLabel("Body threaded length (mm):")
        lbl.setObjectName("Body threaded length")
        damper_layout.addRow(lbl, self.body_threaded_length)

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
        helper_layout.addRow(lbl, self.helper_outer_diam)

        lbl = QtWidgets.QLabel("Helper perch inner diameter (mm):")
        lbl.setObjectName("Helper perch inner diameter")
        helper_layout.addRow(lbl, self.helper_inner_diam)

        lbl = QtWidgets.QLabel("Helper perch thickness (mm):")
        lbl.setObjectName("Helper perch thickness")
        helper_layout.addRow(lbl, self.helper_thickness)

        lbl = QtWidgets.QLabel("Helper perch inner height (mm):")
        lbl.setObjectName("Helper perch inner height")
        helper_layout.addRow(lbl, self.helper_inner_height)

        # Helper spring dimensions

        lbl = QtWidgets.QLabel("Helper spring inner diameter (mm):")
        lbl.setObjectName("Helper spring inner diameter")
        helper_layout.addRow(lbl, self.helper_spring_id)

        lbl = QtWidgets.QLabel("Helper spring outer diameter (mm):")
        lbl.setObjectName("Helper spring inner diameter")
        helper_layout.addRow(lbl, self.helper_spring_od)

        lbl = QtWidgets.QLabel("Helper spring free length (mm):")
        lbl.setObjectName("Helper spring free length")
        helper_layout.addRow(lbl, self.helper_spring_free)

        lbl = QtWidgets.QLabel("Helper spring rate (N/mm):")
        lbl.setObjectName("Helper spring rate")
        helper_layout.addRow(lbl, self.helper_spring_rate)

        lbl = QtWidgets.QLabel("Length at bind (mm):")
        lbl.setObjectName("Length at bind")
        helper_layout.addRow(lbl, self.helper_spring_bind)

        for w in (
            self.helper_above,
            self.helper_below,
            self.helper_outer_diam,
            self.helper_inner_diam,
            self.helper_thickness,
            self.helper_inner_height,
            self.helper_spring_id,
            self.helper_spring_od,
            self.helper_spring_free,
            self.helper_spring_rate,
            self.helper_spring_bind
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
        bump_layout.addRow(lbl, self.bump_height)

        lbl = QtWidgets.QLabel("Bump stop outer diameter (mm):")
        lbl.setObjectName("Bump stop outer diameter")
        bump_layout.addRow(lbl, self.bump_diam)

        lbl = QtWidgets.QLabel("Bump stop spring rate (mm):")
        lbl.setObjectName("Bump stop spring rate")
        bump_layout.addRow(lbl, self.bump_rate)

        for w in (
            self.radio_bump_ext,
            self.radio_bump_int,
            self.bump_height,
            self.bump_diam,
            self.bump_rate,
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
        setup_layout.addRow(lbl, self.perch_input)

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

        # Have the camera center on the top of the damper body
        self.view.opts['center'] = QVector3D(0, 0, self.read_length(self.damper_body_len))
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
            (self.spring_id,    "Inner diameter"),
            (self.spring_wire_dia, "Wire diameter"),
            (self.spring_free,  "Spring free length"),
            (self.spring_rate,  "Spring Rate"),
            (self.spring_bind,  "Length at bind"),
            (self.damper_free,  "Damper free length"),
            (self.damper_compr, "Compressed length"),
            (self.damper_body_len,  "Body length"),
            (self.damper_body_dia,  "Body diameter"),
            (self.damper_shaft_dia, "Shaft diameter"),
            (self.perch_input,  "Spring perch distance"),
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
            self.helper_outer_diam,
            self.helper_inner_diam,
            self.helper_thickness,
            self.helper_inner_height,
            self.helper_spring_id,
            self.helper_spring_od,
            self.helper_spring_free,
            self.helper_spring_rate,
            self.helper_spring_bind
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
            self.bump_height,
            self.bump_diam,
            self.bump_rate,
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
        # read all inputs
        ID      = self.read_length(self.spring_id)
        Dwire   = self.read_length(self.spring_wire_dia)
        L0      = self.read_length(self.spring_free)
        Lbind   = self.read_length(self.spring_bind)
        Dbody   = self.read_length(self.damper_body_dia)
        Lbody   = self.read_length(self.damper_body_len)
        Dshaft  = self.read_length(self.damper_shaft_dia)
        perch   = self.read_length(self.perch_input)
        Lfree   = self.read_length(self.damper_free)
        Lcompr  = self.read_length(self.damper_compr)

        # clear old
        for item in [self.spring_mesh, self.body_mesh, self.shaft_mesh]:
            if item: self.view.removeItem(item)

        # Create damper body
        cyl = self.make_cylinder(Dbody/2, Lbody, 32)
        self.body_mesh = gl.GLMeshItem(
            meshdata=cyl,
            smooth=True, 
            color=(0.4,0.4,0.4,1),
            shader='shaded',         # turn on per‐vertex lighting
            glOptions='opaque',      # so it renders solid faces
            computeNormals=True      # auto-generate normals from faces
        )
        self.body_mesh.translate(0, 0, Lbody/2) # bottom of damper body is the origin
        self.view.addItem(self.body_mesh)

        # Create damper shaft
        shaft = self.make_cylinder(Dshaft/2, self.shaft_length, 16)
        self.shaft_mesh = gl.GLMeshItem(
            meshdata=shaft,
            smooth=True,
            color=(0.8,0.1,0.1,1),
            shader='shaded',         # turn on per‐vertex lighting
            glOptions='opaque',      # so it renders solid faces
            computeNormals=True      # auto-generate normals from faces
        )
        self.shaft_mesh.translate(0, 0, (self.shaft_length/2 + (Lfree - Lcompr)))
        self.view.addItem(self.shaft_mesh)

        # Create spring helix
        self.coils = self.calculate_active_coils(50, Dwire, ID)
        theta  = np.linspace(0, 2*np.pi*self.coils, 200)
        self.spring_x = (ID/2) * np.cos(theta)
        self.spring_y = (ID/2) * np.sin(theta)
        self.theta    = theta

        # store anchor & lengths
        self.bottom_anchor = Lbody + perch + Dwire/2              # world‐Z where spring’s bottom sits
        self.L0            = L0                   # free spring length
        self.Lbind         = Lbind                # coil‑bind length
        self.Dwire         = Dwire
        self.Lfree = Lfree
        self.Lcompr = Lcompr
        self.spring_z0 = 0
        self.spring_z1 = -min(L0 - Lbind, L0)

        # Create GLLinePlotItem for the spring
        z0 = self.bottom_anchor
        z1 = z0 + self.L0
        pts = np.vstack((self.spring_x, self.spring_y, np.linspace(z0, z1, theta.size))).T
        wire = self.make_spring_wire(pts, Dwire/2)
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
        plate_dia        = ID + perch_clearance

        # remove old perch if exists
        if hasattr(self, 'upper_perch'):
            self.view.removeItem(self.upper_perch)
        if hasattr(self, 'upper_cone'):
            self.view.removeItem(self.upper_cone)

        cyl_mesh = self.make_cylinder(plate_dia/2.0, cyl_thickness, sectors=32)
        self.upper_perch = gl.GLMeshItem(
            meshdata=cyl_mesh, smooth=True,
            color=(1.0, 0.5, 0.0, 1.0),
            shader='shaded', glOptions='opaque', computeNormals=True
        )
        # center its bottom on spring_top_z:
        cyl_center_z = Lfree + cyl_thickness/2.0
        self.upper_perch.translate(0, 0, cyl_center_z)
        self.view.addItem(self.upper_perch)

        # Build cone for upper perch
        # Build base ring
        n_segs = 32
        angles = np.linspace(0, 2*np.pi, n_segs, endpoint=False)
        base_pts = np.vstack([
            plate_dia/2.0*np.cos(angles),
            plate_dia/2.0*np.sin(angles),
            np.full_like(angles, Lfree + cyl_thickness)
        ]).T
        # tip vertex
        tip = np.array([0, 0, Lfree + cyl_thickness + cone_height])

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
        plate_dia        = ID + perch_clearance

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
        lower_perch_z = Lbody - cyl_thickness/2.0 + perch
        self.lower_perch.translate(0, 0, lower_perch_z)
        self.view.addItem(self.lower_perch)

        # helper spring perch
        # --- remove old helper perch if present ---
        if hasattr(self, 'helper_perch'):
            self.view.removeItem(self.helper_perch)

        # --- read user inputs (in mm) ---
        th   = self.read_length(self.helper_thickness)            # helper_thickness
        od   = self.read_length(self.helper_outer_diam)   / 2.0   # outer radius
        id_  = self.read_length(self.helper_inner_diam)   / 2.0   # inner radius
        ih   = self.read_length(self.helper_inner_height)        # inner‑height
        self.th = th

        # second ring’s hole radius:
        hole_r = (self.read_length(self.helper_inner_diam) - 2*th) / 2.0

        # --- build the two annular meshes ---
        md1 = self.make_annular_cylinder(od,   id_, th, sectors=64)
        md2 = self.make_annular_cylinder(id_, hole_r, ih, sectors=64)

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

        self.helper_perch.translate(0, 0, (Lbody + perch + L0 + th/2))
        self.view.addItem(self.helper_perch)


        # travel info
        self._perch = perch
        self.animate(self.slider.value())

    def animate(self, t):
        """
        t = 0..100 slider: moves spring + shaft
        """
        f = t / 100

        # Compute current spring length
        Lcurrent   = self.Lfree - (self.Lfree - self.Lcompr) * f
        spring_z0  = self.bottom_anchor

        # Check if spring is loose
        if Lcurrent - (self.Dwire / 2) < (self.bottom_anchor + self.L0):
            spring_z1  = Lcurrent - (self.Dwire / 2)
        else:
            spring_z1 = self.bottom_anchor + self.L0
        spring_length = spring_z1 - spring_z0

        # Check if in coil bind
        if spring_length < self.Lbind:
            spring_length = self.Lbind
            spring_z1 = spring_z0 + self.Lbind
            Lcurrent = spring_z1 + (self.Dwire / 2)

        # Regenerate the helix points & update the line
        zs = np.linspace(spring_z0, spring_z1, self.theta.size)
        pts = np.vstack((self.spring_x, self.spring_y, zs)).T
        new_wire = self.make_spring_wire(pts, self.Dwire/2)
        self.spring_mesh.setMeshData(meshdata=new_wire)

        # Move the shaft so its bottom rests on the spring top
        shaft_center = Lcurrent - self.shaft_length/2
        self.shaft_mesh.resetTransform()
        self.shaft_mesh.translate(0, 0, shaft_center)

        # Move upper spring perch
        self.upper_perch.resetTransform()
        self.upper_perch.translate(0, 0, Lcurrent + 2.5)
        self.upper_cone.resetTransform()
        self.upper_cone.translate(0, 0, (Lcurrent - self.Lfree))

        # Move helper perch
        self.helper_perch.resetTransform()
        self.helper_perch.translate(0, 0, (spring_z1 + (self.Dwire / 2) + (self.th / 2)))


        # Update overlay text
        self.info_label.setText(f"Coilover length: {Lcurrent:.1f} mm\nSpring length: {spring_length:.1f} mm")
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