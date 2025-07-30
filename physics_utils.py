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

import numpy as np

def calculate_active_coils_rectangular(
    spring_rate: float,
    inner_diameter: float,
    outer_diameter: float,
    shear_modulus: float,
    wire_width: float,
    solid_height: float = None
) -> tuple[float, float]:
    """
    Compute number of active coils and rectangular‑wire thickness for a rectangular‑wire coil spring.

    Parameters
    ----------
    spring_rate : float
        Desired spring rate, e.g. N/mm.
    inner_diameter : float
        Inner coil diameter, same units as spring_rate length.
    outer_diameter : float
        Outer coil diameter, same units as spring_rate length.
    shear_modulus : float
        Material shear modulus, same units (e.g. N/mm²).
    wire_width : float
        Rectangular cross‐section width (into the page), same units.
    solid_height : float, optional
        Total spring height at full solid (when coils touch).  If provided,
        the function will solve _both_ n_active and wire_height from the
        solid‐height constraint.  Otherwise it assumes the wire height
        equals (outer_diameter–inner_diameter)/2.

    Returns
    -------
    n_active : float
        Number of active coils required.
    wire_height : float
        Rectangular wire height (radial thickness).

    Notes
    -----
    - We approximate the torsion constant J ≃ wire_width * wire_height³ / 3  
      (valid when the thinner side is ≤ the wider side).
    - Mean coil diameter D_m = (ID + OD) / 2.
    - Spring rate k ≃ G·J / (D_m³·n_active).

    Equations
    ---------
    1) If solid_height is given, we use:
         solid_height = n_active * wire_height
         ⇒ n_active = (G·wire_width·solid_height³ / (3·k·D_m³))^(1/4)
         ⇒ wire_height = solid_height / n_active

    2) Otherwise we set
         wire_height = (outer_diameter - inner_diameter)/2
         J = wire_width * wire_height³ / 3
         ⇒ n_active = G·J / (k·D_m³)
    """
    # mean coil diameter
    D_m = 0.5 * (inner_diameter + outer_diameter)

    if solid_height is not None:
        # solve both n_active and wire_height from solid height
        n_active = (shear_modulus * wire_width * solid_height**3
                    / (3 * spring_rate * D_m**3))**0.25
        wire_height = solid_height / n_active
    else:
        # assume wire fills the radial gap
        wire_height = 0.5 * (outer_diameter - inner_diameter)
        J = wire_width * wire_height**3 / 3.0
        n_active = shear_modulus * J / (spring_rate * D_m**3)

    return n_active, wire_height

def split_strut_length_to_springs(
    k_main: float,
    k_helper: float,
    L_available: float,
    L_bind_main: float,
    L_bind_helper: float,
    L_free_main: float,
    L_free_helper: float
) -> tuple[float, float, float]:
    """
    Distribute a total strut length between two springs in series,
    using free lengths as maxima and bind lengths as minima.

    Returns (L_main, L_helper).
    """
    # Total free length
    L_free_tot = L_free_main + L_free_helper

    # If there's plenty of room, both at free length
    if L_available >= L_free_tot:
        spring_force = 0
        return L_free_main, L_free_helper, spring_force

    # Compute total deflection from free position
    delta_tot = L_free_tot - L_available

    # Series spring force
    spring_force = 1 / (1.0/k_main + 1.0/k_helper) * delta_tot # F = -kx

    # Individual deltas
    delta_main   = spring_force / k_main
    delta_helper = spring_force / k_helper

    # Preliminary lengths
    L_main   = L_free_main   - delta_main
    L_helper = L_free_helper - delta_helper

    # Enforce bind limits (limit whichever hits bind first)
    if L_helper < L_bind_helper:
        # helper has bottomed out
        L_helper = L_bind_helper
        # remaining deflection goes into main
        rem = delta_tot - (L_free_helper - L_bind_helper)
        L_main = max(L_bind_main, L_free_main - rem)
        spring_force = (L_free_main - L_main) * k_main

    elif L_main < L_bind_main:
        L_main = L_bind_main
        rem = delta_tot - (L_free_main - L_bind_main)
        L_helper = max(L_bind_helper, L_free_helper - rem)
        spring_force = (L_free_helper - L_helper) * k_helper

    return L_main, L_helper, spring_force

