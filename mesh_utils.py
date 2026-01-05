import numpy as np
import pyqtgraph.opengl as gl
from physics_utils import compute_frames

def make_cylinder(radius, length, sectors):
    """
    Returns a MeshData cylinder aligned along z.
    """
    theta = np.linspace(0, 2*np.pi, sectors, endpoint=False)
    xs, ys = np.cos(theta)*radius, np.sin(theta)*radius
    # top and bottom circles
    top    = np.vstack([xs, ys, np.full_like(xs, length/2)]).T
    bottom = np.vstack([xs, ys, np.full_like(xs, -length/2)]).T
    top_center = np.array([[0.0, 0.0,  length/2]])
    bot_center = np.array([[0.0, 0.0, -length/2]])

    verts = np.vstack([top, bottom, top_center, bot_center])
    faces = []

    # side faces
    for i in range(sectors):
        n = (i + 1) % sectors
        faces.append([i, n, sectors + i])
        faces.append([n, sectors + n, sectors + i])

    top_c_idx = 2 * sectors
    bot_c_idx = 2 * sectors + 1

    # top cap (normals point +Z)
    for i in range(sectors):
        n = (i + 1) % sectors
        faces.append([top_c_idx, i, n])

    # bottom cap (normals point -Z)
    for i in range(sectors):
        n = (i + 1) % sectors
        faces.append([bot_c_idx, sectors + n, sectors + i])

    return gl.MeshData(vertexes=verts, faces=np.array(faces))

def make_annular_cylinder(outer_r, inner_r, height, sectors=32):
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

def make_spring_wire(path_pts, wire_radius, n_sides=8):
        """
        Sweeps along the spring helix to create the spring geometry
        path_pts: (N,3) array of helix points
        wire_radius: radius of spring wire in same units as path_pts
        returns: MeshData for a tube
        """
        tangents, normals, binorms = compute_frames(path_pts)
        
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
        for i in range(len(path_pts) - 1):
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

def make_rectangular_spring_wire(path_pts, wire_width, wire_height):
    """
    Sweeps along the spring helix to create a rectangular-wire spring
    whose cross-section remains upright (parallel to XY ground plane).

    path_pts: (N,3) array of helix centerline points
    wire_width: width of the rectangular cross-section (radial direction)
    wire_height: height of the rectangular cross-section (vertical)
    returns: MeshData for a rectangular prism sweep
    """
    # we only need tangents; normals/binorms no longer used for section orientation
    tangents, _, _ = compute_frames(path_pts)

    # Predefine the 4 local corner offsets in (radial, vertical) coords
    local_corners = [
        (+wire_width/2, +wire_height/2),
        (-wire_width/2, +wire_height/2),
        (-wire_width/2, -wire_height/2),
        (+wire_width/2, -wire_height/2),
    ]

    verts = []
    faces = []
    global_up = np.array([0.0, 0.0, 1.0])

    # Build vertices
    for i, p in enumerate(path_pts):
        t = tangents[i]
        # radial axis: perpendicular to both tangent and up
        r = np.cross(global_up, t)
        norm_r = np.linalg.norm(r)
        if norm_r < 1e-6:
            # tangent is nearly vertical → choose arbitrary horizontal axis
            r = np.array([1.0, 0.0, 0.0])
        else:
            r /= norm_r

        # vertical axis in the plane normal to tangent
        v = np.cross(t, r)
        v /= np.linalg.norm(v)

        # place each corner
        for (wx, hy) in local_corners:
            offset = r * wx + v * hy
            verts.append(p + offset)

    verts = np.array(verts)  # shape (N*4, 3)

    # Build faces by connecting quads between successive sections
    n_sections = len(path_pts)
    for i in range(n_sections - 1):
        for j in range(4):
            a =  i*4 + j
            b =  i*4 + (j + 1) % 4
            c = (i+1)*4 + j
            d = (i+1)*4 + (j + 1) % 4
            # two triangles per quad
            faces.append([a, c, b])
            faces.append([b, c, d])

    return gl.MeshData(vertexes=verts, faces=np.array(faces))
