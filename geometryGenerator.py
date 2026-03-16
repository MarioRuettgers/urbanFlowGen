import trimesh
import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from shapely.affinity import rotate
import trimesh.creation
import trimesh.exchange.stl
import json
import random
import sys
import os
import toml

# Parts of the geometry
# Inlet - I
# Outlet - II
# Left - III
# Right - IV
# Top - V
# Bottom around plate - VI
# Bottom plate - VII
# Buildings - VIII

# Load configuration file
config_path = 'config.toml'
params = toml.load(config_path)

#--- User input ---
if len(sys.argv) < 2:
    raise ValueError("Missing required argument: sample_id")
sample_id = int(sys.argv[1])  # USER-DEFINED SAMPLE ID
stl_path = os.path.join('.', str(sample_id), 'stl')
geometry_path = os.path.join('.', str(sample_id))

# Global bounds
x_min = params['global']['x_min']
x_max = params['global']['x_max']
y_min = params['global']['y_min']
y_max = params['global']['y_max']
z_min = params['global']['z_min']
z_max = params['global']['z_max']

# Bottom center bounds
x_min_VII = params['bottom_center']['x_min_VII']
x_max_VII = params['bottom_center']['x_max_VII']
y_min_VII = params['bottom_center']['y_min_VII']
y_max_VII = params['bottom_center']['y_max_VII']

# Safety distances
sd_x_neg = params['safety']['sd_x_neg']
sd_x_pos = params['safety']['sd_x_pos']
sd_y = params['safety']['sd_y']
md   = params['safety']['md']

# Number of buildings
b_min = params['buildings']['b_min']
b_max = params['buildings']['b_max']

# Rectangular buildings
l_min  = params['rectangular']['l_min']
l_max  = params['rectangular']['l_max']
a_max  = params['rectangular']['a_max']

# Extreme buildings
P_E      = params['extreme']['P_E']
e_max  = params['extreme']['e_max']

# Circular buildings
P_C      = params['circular']['P_C']
d_min  = params['circular']['d_min']
d_max  = params['circular']['d_max']
phi    = params['circular']['phi']

# Heights
h_min  = params['height']['h_min']
h_max  = params['height']['h_max']

# Towers
P_T      = params['towers']['P_T']
t_min  = params['towers']['t_min']
t_max  = params['towers']['t_max']
s_min  = params['towers']['s_min']
s_max  = params['towers']['s_max']
w_max  = params['towers']['w_max']

# Roads
r       = params['roads']['r']
rx_min  = params['roads']['rx_min']
rx_max  = params['roads']['rx_max']
ry_min  = params['roads']['ry_min']
ry_max  = params['roads']['ry_max']

def make_patch(v0, v1, v2, v3):
    """Create a rectangular patch mesh from four corner vertices."""
    vertices = np.array([v0, v1, v2, v3])
    faces = np.array([[0, 1, 2], [0, 2, 3]])
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

######################################
# Inlet - I
######################################
inlet = make_patch(
    [x_min, y_min, z_min],
    [x_min, y_max, z_min],
    [x_min, y_max, z_max],
    [x_min, y_min, z_max]
)
inlet.export(os.path.join(stl_path, 'inlet.stl'), file_type='stl_ascii')

######################################
# Outlet - II
######################################
outlet = make_patch(
    [x_max, y_min, z_min],
    [x_max, y_max, z_min],
    [x_max, y_max, z_max],
    [x_max, y_min, z_max]
)
outlet.export(os.path.join(stl_path, 'outlet.stl'), file_type='stl_ascii')

######################################
# Left - III
######################################
left = make_patch(
    [x_min, y_max, z_min],
    [x_max, y_max, z_min],
    [x_max, y_max, z_max],
    [x_min, y_max, z_max]
)
left.export(os.path.join(stl_path, 'left.stl'), file_type='stl_ascii')

######################################
# Right - IV
######################################
right = make_patch(
    [x_min, y_min, z_min],
    [x_max, y_min, z_min],
    [x_max, y_min, z_max],
    [x_min, y_min, z_max]
)
right.export(os.path.join(stl_path, 'right.stl'), file_type='stl_ascii')

######################################
# Top - V
######################################
top = make_patch(
    [x_min, y_min, z_max],
    [x_max, y_min, z_max],
    [x_max, y_max, z_max],
    [x_min, y_max, z_max]
)
top.export(os.path.join(stl_path, 'top.stl'), file_type='stl_ascii')

######################################
# Bottom surround plate - VI
######################################
# This part reuses the `make_patch()` from earlier message
bottom_surround = trimesh.util.concatenate([
    # Left of plate
    make_patch(
        [x_min,     y_min,     z_min],
        [x_min_VII, y_min,     z_min],
        [x_min_VII, y_max,     z_min],
        [x_min,     y_max,     z_min]
    ),
    # Right of plate
    make_patch(
        [x_max_VII, y_min,     z_min],
        [x_max,     y_min,     z_min],
        [x_max,     y_max,     z_min],
        [x_max_VII, y_max,     z_min]
    ),
    # Front of plate
    make_patch(
        [x_min_VII, y_max_VII, z_min],
        [x_max_VII, y_max_VII, z_min],
        [x_max_VII, y_max,     z_min],
        [x_min_VII, y_max,     z_min]
    ),
    # Back of plate
    make_patch(
        [x_min_VII, y_min,     z_min],
        [x_max_VII, y_min,     z_min],
        [x_max_VII, y_min_VII, z_min],
        [x_min_VII, y_min_VII, z_min]
    )
])
bottom_surround.export(os.path.join(stl_path, 'bottom_around_plate.stl'), file_type='stl_ascii')

######################################
# Bottom plate - VII
# Buildings - VIII 
######################################
# --- 1. Rotation setup ---
angle_deg = np.random.uniform(0, 90)
angle_rad = np.deg2rad(angle_deg)

# Get center of the plate
plate_center = np.array([
    (x_min_VII + x_max_VII) / 2,
    (y_min_VII + y_max_VII) / 2
])

def rotate_points(points, angle_rad, center):
    """
    Rotate a 2D point or array of points around a center by a given angle in radians.
    """
    points = np.atleast_2d(points)
    R = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad),  np.cos(angle_rad)]
    ])
    return (points - center) @ R.T + center


# --- 2. Outer plane polygon ---
outer = Polygon([
    [x_min_VII, y_min_VII],
    [x_max_VII, y_min_VII],
    [x_max_VII, y_max_VII],
    [x_min_VII, y_max_VII]
])

# --- 3. Generate random road network ---
def generate_random_roads(x_min_VII, x_max_VII, y_min_VII, y_max_VII, r):
    global num_vertical_roads, num_horizontal_roads
    num_vertical_roads = np.random.randint(ry_min, ry_max)
    num_horizontal_roads = np.random.randint(rx_min, rx_max)

    vertical_positions = np.sort(np.random.uniform(x_min_VII + sd_x_neg, x_max_VII - sd_x_pos, num_vertical_roads))
    horizontal_positions = np.sort(np.random.uniform(y_min_VII + sd_y, y_max_VII - sd_y, num_horizontal_roads))

    vertical_roads = [
        LineString([[x, y_min_VII], [x, y_max_VII]]).buffer(r / 2)
        for x in vertical_positions
    ]
    horizontal_roads = [
        LineString([[x_min_VII, y], [x_max_VII, y]]).buffer(r / 2)
        for y in horizontal_positions
    ]

    return vertical_roads + horizontal_roads

roads = generate_random_roads(x_min_VII, x_max_VII, y_min_VII, y_max_VII, r)
origin=tuple(plate_center)
rotated_roads = [rotate(road, angle_deg, origin=origin) for road in roads]
road_union = unary_union(rotated_roads)

# --- 4. Generate building footprints ---
def random_building_footprint():
    shape = 'rect'
    if np.random.rand() < P_C:
        diameter = np.random.uniform(d_min, d_max)
        height = np.random.uniform(h_min, h_max)
        shape = 'circle'
        return diameter, diameter, height, shape

    if np.random.rand() < P_T:
        for _ in range(100):
            w = np.random.uniform(t_min, t_max)
            h = np.random.uniform(t_min, t_max)
            if max(w / h, h / w) <= w_max:
                height = np.random.uniform(s_min, s_max)
                return w, h, height, shape
    else:
        for _ in range(100):
            w = np.random.uniform(l_min, l_max)
            h = np.random.uniform(l_min, l_max)
            aspect = max(w / h, h / w)
            limit = e_max if np.random.rand() < P_E else a_max
            if aspect <= limit:
                height = np.random.uniform(h_min, h_max)
                return w, h, height, shape
    raise ValueError("Couldn't generate a valid building footprint.")

# --- 5. Generate buildings ---
num_buildings = np.random.randint(b_min, b_max)
holes = []
positions = []
sizes = []
heights = []
shapes = []

attempts = 0
max_attempts = 1000



while len(holes) < num_buildings and attempts < max_attempts:
    attempts += 1
    w, h, height, shape = random_building_footprint()
    diag = np.sqrt(w**2 + h**2)
    buffer_x_neg = sd_x_neg + diag / 2
    buffer_x_pos = sd_x_pos + diag / 2
    buffer_y = sd_y + diag / 2

    x_range = (x_min_VII + buffer_x_neg, x_max_VII - buffer_x_pos)
    y_range = (y_min_VII + buffer_y, y_max_VII - buffer_y)

    initial_pos = np.array([
        np.random.uniform(*x_range),
        np.random.uniform(*y_range)
    ])
    
    if shape == 'circle':
        radius = w / 2
        theta = np.linspace(0, 2 * np.pi, phi , endpoint=False)
        circle_points = np.column_stack([np.cos(theta), np.sin(theta)]) * radius
        # Rotate the shape around origin (it’s local), then place at rotated position
        rotated_circle = rotate_points(circle_points, angle_rad, np.array([0, 0])) + initial_pos
        hole_poly = Polygon(rotated_circle)

    else:
        hw, hh = w / 2, h / 2
        local_rect = np.array([
            [-hw, -hh],
            [ hw, -hh],
            [ hw,  hh],
            [-hw,  hh]
        ])
        rotated_rect = rotate_points(local_rect, angle_rad, np.array([0, 0])) + initial_pos
        hole_poly = Polygon(rotated_rect)

    if not outer.contains(hole_poly):
        continue
    
    buffered_hole = hole_poly.buffer(md)
    if any(buffered_hole.intersects(existing) for existing in holes):
       continue
    
    if hole_poly.intersects(road_union):
        continue

    holes.append(hole_poly)
    positions.append(initial_pos)
    sizes.append((w, h))
    heights.append(height)
    shapes.append(shape)

# --- 6. Create polygon with holes ---
polygon_with_holes = Polygon(outer.exterior.coords, holes=[h.exterior.coords for h in holes])
tri_data = trimesh.creation.triangulate_polygon(polygon_with_holes)

if isinstance(tri_data, tuple):
    vertices_2d, faces = tri_data
    vertices_3d = np.column_stack((vertices_2d, np.full(len(vertices_2d), z_min)))
    surface_mesh = trimesh.Trimesh(vertices=vertices_3d, faces=faces, process=False)
else:
    surface_mesh = tri_data
    surface_mesh.apply_translation([0, 0, z_min])

# --- 7. Create building meshes ---
cylinders = []

for (w, h), height, pos, shape in zip(sizes, heights, positions, shapes):
    if shape == 'circle':
        radius = w / 2
        building = trimesh.creation.cylinder(radius=radius, height=height, sections=phi)
    else:
        building = trimesh.creation.box(extents=(w, h, height))

    normals = building.face_normals
    keep_faces = np.where(normals[:, 2] > -0.9)[0]
    building_open = building.submesh([keep_faces], append=True)

    building_open.apply_transform(trimesh.transformations.rotation_matrix(
        angle_rad, [0, 0, 1]
    ))
    building_open.apply_translation([*pos, z_min + height / 2])
    cylinders.append(building_open)

# --- 8. Combine and export STL ---

# Combine buildings into one mesh
buildings_mesh = trimesh.util.concatenate(cylinders)

# Define filenames
plane_filename = os.path.join(stl_path, f'bottom_plate_{sample_id}.stl')
buildings_filename = os.path.join(stl_path, f'buildings_{sample_id}.stl')

# Export plane mesh (single mesh, not a list)
with open(plane_filename, 'w') as f:
    f.write(trimesh.exchange.stl.export_stl_ascii(surface_mesh))

# Export buildings mesh
with open(buildings_filename, 'w') as f:
    f.write(trimesh.exchange.stl.export_stl_ascii(buildings_mesh))

#filename = os.path.join(stl_path,f'{sample_id}.stl')
#with open(filename, 'w') as f:
#    f.write(trimesh.exchange.stl.export_stl_ascii(trimesh.util.concatenate([surface_mesh] + cylinders)))

# --- 9. Save metadata to JSON ---
metadata = {
    "sample_id": sample_id,
    "rotation_angle_deg": round(angle_deg, 2),
    "domain": {"x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max},
    "bounds_for_x_of_section_VII": {"x_min_VII": x_min_VII, "x_max_VII": x_max_VII},
    "bounds_for_y_of_section_VII": {"y_min_VII": y_min_VII, "y_max_VII": y_max_VII},
    "safety_distance_x_negative": sd_x_neg,
    "safety_distance_x_positive": sd_x_pos,
    "safety_distance_y": sd_y,
    "min_building_distance": md,
    "bounds_for_nr_of_buildings": [b_min, b_max],
    "building_count": len(cylinders),
    "rectangular_building_size_range": [l_min, l_max],
    "extreme_aspect_chance": P_E,
    "aspect_ratio_limits_rectangular_buildings": {
        "normal_max": a_max,
        "extreme_max": e_max
    },
    "circle_chance": P_C,
    "circular_building_size_range": [d_min, d_max],
    "circle_resolution": phi,
    "building_height_range": [h_min, h_max],
    "tower_chance": P_T,
    "tower_size_range": [t_min, t_max],
    "tower_height_range": [s_min, s_max],
    "tower_max_aspect_ratio": w_max,
    "road_width": r,
    "bounds_for_nr_of_horizontal_roads": [rx_min, rx_max],
    "bounds_for_nr_of_vertical_roads": [ry_min, ry_max],
    "vertical_road_count": num_vertical_roads,
    "horizontal_road_count": num_horizontal_roads,
    "building_shapes": shapes,
    "building_sizes": sizes,
    "building_heights": heights,
    "building_positions": [pos.tolist() for pos in positions]
}

with open(os.path.join(stl_path,f'{sample_id}_metadata.json'), 'w') as f:
    json.dump(metadata, f, indent=4)

# --- 10. Summary info ---
print(f"Plane mesh saved to: {plane_filename}")
print(f"Buildings mesh saved to: {buildings_filename}")
print(f"Metadata saved: {sample_id}_metadata.json")
print(f"Buildings: {len(cylinders)} | Rotation: {angle_deg:.2f}°")

# --- 11. Generate "geometry.toml" ---
def generate_geometry_toml(x: int, output_file: str = "geometry.toml"):
    # Fixed STL filenames except the two dynamic ones
    filenames = {
        0: "./stl/inlet.stl",
        1: "./stl/outlet.stl",
        2: "./stl/left.stl",
        3: "./stl/right.stl",
        4: "./stl/top.stl",
        5: "./stl/bottom_around_plate.stl",
        6: f"./stl/bottom_plate_{x}.stl",
        7: f"./stl/buildings_{x}.stl"
    }

    # Boundary conditions
    bc = {
        0: 1000,
        1: 4000,
        2: 3020,
        3: 3020,
        4: 3020,
        5: 3020,
        6: 2000,
        7: 2000
    }

    # Segment name to index mapping
    body_segments = {
        "body_segments.inlet": 0,
        "body_segments.outlet": 1,
        "body_segments.left": 2,
        "body_segments.right": 3,
        "body_segments.top": 4,
        "body_segments.bottom_around_plate": 5,
        "body_segments.bottom_plate": 6,
        "body_segments.buildings": 7
    }

    # Assemble dictionary for TOML
    geometry = {
        "noSegments": 8,
        "inOutSegmentsIds": [0, 1],
    }

    # Add filenames
    for idx, fname in filenames.items():
        geometry[f"filename.{idx}"] = fname

    # Add body segment mapping
    geometry.update(body_segments)

    # Add boundary conditions
    for idx, val in bc.items():
        geometry[f"BC.{idx}"] = val

    # Write to TOML file
    with open(os.path.join(geometry_path,output_file), "w") as f:
        toml.dump(geometry, f)

    print(f"geometry.toml generated (x = {x})")

generate_geometry_toml(x=sample_id)
