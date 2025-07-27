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

        # 2) Spring group
        spring_group   = QtWidgets.QGroupBox("Spring")
        spring_layout  = QtWidgets.QFormLayout()
        spring_layout.addRow("Inner diameter (mm):",   self.spring_id)
        spring_layout.addRow("Free length (mm):",      self.spring_free)
        spring_layout.addRow("Rate (N/mm):",           self.spring_rate)
        spring_layout.addRow("Length at bind (mm):",   self.spring_bind)
        spring_group.setLayout(spring_layout)

        # 3) Damper group
        damper_group  = QtWidgets.QGroupBox("Damper")
        damper_layout = QtWidgets.QFormLayout()
        damper_layout.addRow("Free length (mm):",           self.damper_free)
        damper_layout.addRow("Compressed length (mm):",     self.damper_compr)
        damper_layout.addRow("Body length (mm):",           self.damper_body_len)
        damper_layout.addRow("Body diameter (mm):",         self.damper_body_dia)
        damper_layout.addRow("Shaft diameter (mm):",        self.damper_shaft_dia)
        damper_group.setLayout(damper_layout)

        # 4) Perch distance (still its own entry)
        self.perch_input = QtWidgets.QLineEdit("10")
        perch_label = QtWidgets.QLabel("Spring perch dist. (mm):")

        # 5) Assemble left‐side layout
        left_layout = QtWidgets.QVBoxLayout()
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

    def update_view(self):
        # read inputs
        ID      = float(self.spring_id.text()) 
        L0      = float(self.spring_free.text())
        Lbind   = float(self.spring_bind.text())
        Dbody   = float(self.damper_body_dia.text())
        Lbody   = float(self.damper_body_len.text())
        Dshaft  = float(self.damper_shaft_dia.text())
        perch   = float(self.perch_input.text())
        Lfree   = float(self.damper_free.text())
        Lcompr  = float(self.damper_compr.text())

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