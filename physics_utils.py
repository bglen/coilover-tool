import numpy as np

def calculate_active_coils(spring_rate, wire_diameter, inner_diameter, shear_modulus=80000):
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

def compute_frames(path_pts):
    """
    Compute tangent, normal, binormal frames via parallel transport.
    """
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
    for i in range(1, len(path_pts)):
        # make sure normals stay orthogonal to new tangent:
        v = normals[i-1] - tangents[i] * np.dot(tangents[i], normals[i-1])
        normals[i] = v / np.linalg.norm(v)
        binorms[i] = np.cross(tangents[i], normals[i])
    return tangents, normals, binorms