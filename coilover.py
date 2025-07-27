import sys
import numpy as np

from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl

class CoiloverDesigner(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coilover Tool")
        self.resize(1000, 600)

        # ─── Left panel: parameter inputs ────────────────────────────
        form = QtWidgets.QFormLayout()
        self.spring_id        = QtWidgets.QLineEdit("60")   # mm
        self.spring_free      = QtWidgets.QLineEdit("200")  # mm
        self.spring_rate      = QtWidgets.QLineEdit("100")  # N/mm
        self.spring_bind      = QtWidgets.QLineEdit("50")   # mm
        self.damper_free      = QtWidgets.QLineEdit("300")  # mm
        self.damper_compr     = QtWidgets.QLineEdit("250")  # mm
        self.damper_body_len  = QtWidgets.QLineEdit("200")  # mm
        self.damper_body_dia  = QtWidgets.QLineEdit("50")   # mm
        self.damper_shaft_dia = QtWidgets.QLineEdit("20")   # mm
        self.perch_input      = QtWidgets.QLineEdit("10")   # mm
        self.shaft_length     = float(self.damper_compr.text())
        self.coils = 10
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

        damper_group.setLayout(damper_layout)

        # System
        self.perch_input = QtWidgets.QLineEdit("10")
        perch_label = QtWidgets.QLabel("Spring perch distance (mm):")
        perch_label.setObjectName("Spring perch distance")

        # Assemble left‐side layout
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(settings_group)
        left_layout.addWidget(spring_group)
        left_layout.addWidget(damper_group)

        # optional separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        left_layout.addWidget(separator)

        # perch + update button
        left_layout.addWidget(perch_label)
        left_layout.addWidget(self.perch_input)
        update_btn = QtWidgets.QPushButton("Update View")
        update_btn.clicked.connect(self.update_view)
        left_layout.addWidget(update_btn, alignment=QtCore.Qt.AlignTop)

        left = QtWidgets.QWidget()
        left.setLayout(left_layout)

        btn = QtWidgets.QPushButton("Update View")
        btn.clicked.connect(self.update_view)
        form.addRow(btn)

        # ─── Right panel: 3D view ───────────────────────────────────
        self.view = gl.GLViewWidget()
        self.view.opts['distance'] = 600
        self.view.setBackgroundColor('#181818')

        # axes for reference
        axis = gl.GLAxisItem()
        axis.setSize(100,100,100)
        self.view.addItem(axis)

        # slider for travel
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
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
        splitter.addWidget(left)
        splitter.addWidget(w)
        self.setCentralWidget(splitter)

        # placeholders
        self.spring_mesh = None
        self.body_mesh   = None
        self.shaft_mesh  = None

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

    def read_length(self, widget):
        val = float(widget.text())
        if self.unit == "in":
            return val * 25.4  # convert inches back to mm
        return val            # already in mm

    def update_view(self):
        # read inputs
        ID      = self.read_length(self.spring_id)
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
        self.body_mesh = gl.GLMeshItem(meshdata=cyl, smooth=True, color=(0.4,0.4,0.4,1))
        self.body_mesh.translate(0, 0, Lbody/2) # bottom of damper body is the origin
        self.view.addItem(self.body_mesh)

        # Create damper shaft
        shaft = self.make_cylinder(Dshaft/2, self.shaft_length, 16)
        self.shaft_mesh = gl.GLMeshItem(meshdata=shaft, smooth=True, color=(0.8,0.1,0.1,1))
        self.shaft_mesh.translate(0, 0, (Lfree - self.shaft_length/2))
        self.view.addItem(self.shaft_mesh)

        # Create spring helix
        theta  = np.linspace(0, 2*np.pi*self.coils, 200)
        self.spring_x = (ID/2) * np.cos(theta)
        self.spring_y = (ID/2) * np.sin(theta)
        self.theta    = theta

        # store anchor & lengths
        self.bottom_anchor = Lbody + perch              # world‐Z where spring’s bottom sits
        self.L0            = L0                   # free spring length
        self.Lbind         = Lbind                # coil‑bind length

        # Create GLLinePlotItem for the spring
        z0 = self.bottom_anchor
        z1 = z0 + self.L0
        pts = np.vstack((self.spring_x, self.spring_y, np.linspace(z0, z1, theta.size))).T
        self.spring_mesh = gl.GLLinePlotItem(pos=pts, width=2, color=(0.1,0.1,0.8,1))
        self.view.addItem(self.spring_mesh)

        # travel info
        self.spring_z0 = 0
        self.spring_z1 = -min(L0 - Lbind, L0)
        self._perch = perch
        self.animate(self.slider.value())

    def animate(self, t):
        """
        t = 0..100 slider: moves spring + shaft
        """
        f = t / 100

        # 1) compute current spring length
        Lcurrent   = self.L0 - (self.L0 - self.Lbind) * f
        spring_z0  = self.bottom_anchor
        spring_z1  = spring_z0 + Lcurrent

        # 2) regenerate the helix points & update the line
        zs = np.linspace(spring_z0, spring_z1, self.theta.size)
        pts = np.vstack((self.spring_x, self.spring_y, zs)).T
        self.spring_mesh.setData(pos=pts)

        # 3) reposition the shaft so its *bottom* rests on the spring top
        shaft_center = spring_z1 - self.shaft_length/2
        self.shaft_mesh.resetTransform()
        self.shaft_mesh.translate(0, 0, shaft_center)

        # if self.shaft_mesh:
            # move shaft up as damper compresses
            # self.shaft_mesh.resetTransform()
            #self.shaft_mesh.translate(0, 0, -self._perch * (t / 100))

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