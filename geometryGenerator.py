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
# Bottom front - VI
# Bottom back - VII
# Bottom center - VIII

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
x_min_VIII = params['bottom_center']['x_min_VIII']
x_max_VIII = params['bottom_center']['x_max_VIII']

# Safety distances
sd_x = params['safety']['sd_x']
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
E      = params['extreme']['E']
e_max  = params['extreme']['e_max']

# Circular buildings
C      = params['circular']['C']
d_min  = params['circular']['d_min']
d_max  = params['circular']['d_max']
phi    = params['circular']['phi']

# Heights
h_min  = params['height']['h_min']
h_max  = params['height']['h_max']

# Towers
T      = params['towers']['T']
t_min  = params['towers']['t_min']
t_max  = params['towers']['t_max']
s_min  = params['towers']['s_min']
s_max  = params['towers']['s_max']
w_max  = params['towers']['w_max']

# Roads
r       = params['roads']['r']
rh_min  = params['roads']['rh_min']
rh_max  = params['roads']['rh_max']
rv_min  = params['roads']['rv_min']
rv_max  = params['roads']['rv_max']


######################################
# Inlet - I 
######################################
# Define the four corner vertices of the rectangle at x = 0
vertices = np.array([
    [x_min, y_min, z_min],
    [x_min, y_max, z_min],
    [x_min, y_max, z_max],
    [x_min, y_min, z_max]
])

# Define two triangles that make up the rectangle
faces = np.array([
    [0, 1, 2],
    [0, 2, 3]
])

# Create a mesh
plane = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

# Export to ASCII STL
plane.export(os.path.join(stl_path,'inlet.stl'), file_type='stl_ascii')

######################################
# Outlet - II 
######################################
# Define the four corner vertices of the rectangle at x = 0
vertices = np.array([
    [x_max, y_min, z_min],
    [x_max, y_max, z_min],
    [x_max, y_max, z_max],
    [x_max, y_min, z_max]
])

# Define two triangles that make up the rectangle
faces = np.array([
    [0, 1, 2],
    [0, 2, 3]
])

# Create a mesh
plane = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

# Export to ASCII STL
plane.export(os.path.join(stl_path,'outlet.stl'), file_type='stl_ascii')

######################################
# Left - III 
######################################
# Define the four corner vertices of the rectangle at x = 0
vertices = np.array([
    [x_min, y_max, z_min],
    [x_max, y_max, z_min],
    [x_max, y_max, z_max],
    [x_min, y_max, z_max]
])

# Define two triangles that make up the rectangle
faces = np.array([
    [0, 1, 2],
    [0, 2, 3]
])

# Create a mesh
plane = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

# Export to ASCII STL
plane.export(os.path.join(stl_path,'left.stl'), file_type='stl_ascii')

######################################
# Right - IV
######################################
# Define the four corner vertices of the rectangle at x = 0
vertices = np.array([
    [x_min, y_min, z_min],
    [x_max, y_min, z_min],
    [x_max, y_min, z_max],
    [x_min, y_min, z_max]
])

# Define two triangles that make up the rectangle
faces = np.array([
    [0, 1, 2],
    [0, 2, 3]
])

# Create a mesh
plane = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

# Export to ASCII STL
plane.export(os.path.join(stl_path,'right.stl'), file_type='stl_ascii')

######################################
# Top - V
######################################
# Define the four corner vertices of the rectangle at x = 0
vertices = np.array([
    [x_min, y_min, z_max],
    [x_max, y_min, z_max],
    [x_max, y_max, z_max],
    [x_min, y_max, z_max]
])

# Define two triangles that make up the rectangle
faces = np.array([
    [0, 1, 2],
    [0, 2, 3]
])

# Create a mesh
plane = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

# Export to ASCII STL
plane.export(os.path.join(stl_path,'top.stl'), file_type='stl_ascii')

######################################
# Bottom front - VI
######################################
# Define the four corner vertices of the rectangle at x = 0
vertices = np.array([
    [x_min, y_min, z_min],
    [x_min_VIII, y_min, z_min],
    [x_min_VIII, y_max, z_min],
    [x_min, y_max, z_min]
])

# Define two triangles that make up the rectangle
faces = np.array([
    [0, 1, 2],
    [0, 2, 3]
])

# Create a mesh
plane = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

# Export to ASCII STL
plane.export(os.path.join(stl_path,'bottom_front.stl'), file_type='stl_ascii')

######################################
# Bottom back - VII
######################################
# Define the four corner vertices of the rectangle at x = 0
vertices = np.array([
    [x_max, y_min, z_min],
    [x_max_VIII, y_min, z_min],
    [x_max_VIII, y_max, z_min],
    [x_max, y_max, z_min]
])

# Define two triangles that make up the rectangle
faces = np.array([
    [0, 1, 2],
    [0, 2, 3]
])

# Create a mesh
plane = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

# Export to ASCII STL
plane.export(os.path.join(stl_path,'bottom_back.stl'), file_type='stl_ascii')

######################################
# Wall bottom center (no-slip) - VIII 
######################################
# --- 1. Rotation setup ---
angle_deg = np.random.uniform(0, 90)
angle_rad = np.deg2rad(angle_deg)

R = np.array([
    [np.cos(angle_rad), -np.sin(angle_rad)],
    [np.sin(angle_rad),  np.cos(angle_rad)]
])

# --- 2. Outer plane polygon ---
outer = Polygon([
    [x_min_VIII, y_min],
    [x_max_VIII, y_min],
    [x_max_VIII, y_max],
    [x_min_VIII, y_max]
])

# --- 3. Generate random road network ---
def generate_random_roads(x_min_VIII, x_max_VIII, y_min, y_max, r):
    global num_vertical_roads, num_horizontal_roads
    num_vertical_roads = np.random.randint(rv_min, rv_max)
    num_horizontal_roads = np.random.randint(rh_min, rh_max)

    vertical_positions = np.sort(np.random.uniform(x_min_VIII + sd_x, x_max_VIII - sd_x, num_vertical_roads))
    horizontal_positions = np.sort(np.random.uniform(y_min + sd_y, y_max - sd_y, num_horizontal_roads))

    vertical_roads = [
        LineString([[x, y_min], [x, y_max]]).buffer(r / 2)
        for x in vertical_positions
    ]
    horizontal_roads = [
        LineString([[x_min_VIII, y], [x_max_VIII, y]]).buffer(r / 2)
        for y in horizontal_positions
    ]

    return vertical_roads + horizontal_roads

roads = generate_random_roads(x_min_VIII, x_max_VIII, y_min, y_max, r)
rotated_roads = [rotate(road, angle_deg, origin=(0, 0)) for road in roads]
road_union = unary_union(rotated_roads)

# --- 4. Generate building footprints ---
def random_building_footprint():
    shape = 'rect'
    if np.random.rand() < C:
        diameter = np.random.uniform(d_min, d_max)
        height = np.random.uniform(h_min, h_max)
        shape = 'circle'
        return diameter, diameter, height, shape

    if np.random.rand() < T:
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
            limit = e_max if np.random.rand() < E else a_max
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
    buffer_x = sd_x + diag / 2
    buffer_y = sd_y + diag / 2

    x_range = (x_min_VIII + buffer_x, x_max_VIII - buffer_x)
    y_range = (y_min + buffer_y, y_max - buffer_y)

    initial_pos = np.array([
        np.random.uniform(*x_range),
        np.random.uniform(*y_range)
    ])
    rotated_pos = initial_pos @ R.T

    if shape == 'circle':
        radius = w / 2
        theta = np.linspace(0, 2 * np.pi, phi , endpoint=False)
        circle_points = np.column_stack([np.cos(theta), np.sin(theta)]) * radius
        rotated_circle = circle_points @ R.T + rotated_pos
        hole_poly = Polygon(rotated_circle)
    else:
        hw, hh = w / 2, h / 2
        local_rect = np.array([
            [-hw, -hh],
            [ hw, -hh],
            [ hw,  hh],
            [-hw,  hh]
        ])
        rotated_rect = local_rect @ R.T + rotated_pos
        hole_poly = Polygon(rotated_rect)

    if not outer.contains(hole_poly):
        continue
    
    buffered_hole = hole_poly.buffer(md)
    if any(buffered_hole.intersects(existing) for existing in holes):
       continue
    
    if hole_poly.intersects(road_union):
        continue

    holes.append(hole_poly)
    positions.append(rotated_pos)
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
plane_filename = os.path.join(stl_path, f'bottom_center_{sample_id}.stl')
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
    "bounds_for_x_of_section_VIII": {"x_min_VIII": x_min_VIII, "x_max_VIII": x_max_VIII},
    "safety_distance_x": sd_x,
    "safety_distance_y": sd_y,
    "min_building_distance": md,
    "bounds_for_nr_of_buildings": [b_min, b_max],
    "building_count": len(cylinders),
    "rectangular_building_size_range": [l_min, l_max],
    "extreme_aspect_chance": E,
    "aspect_ratio_limits_rectangular_buildings": {
        "normal_max": a_max,
        "extreme_max": e_max
    },
    "circle_chance": C,
    "circular_building_size_range": [d_min, d_max],
    "circle_resolution": phi,
    "building_height_range": [h_min, h_max],
    "tower_chance": T,
    "tower_size_range": [t_min, t_max],
    "tower_height_range": [s_min, s_max],
    "tower_max_aspect_ratio": w_max,
    "road_width": r,
    "bounds_for_nr_of_horizontal_roads": [rh_min, rh_max],
    "bounds_for_nr_of_vertical_roads": [rv_min, rv_max],
    "vertical_road_count": num_vertical_roads,
    "horizontal_road_count": num_horizontal_roads,
    "building_shapes": shapes,
    "building_sizes": sizes,
    "building_heights": heights
}

with open(os.path.join(stl_path,f'{sample_id}_metadata.json'), 'w') as f:
    json.dump(metadata, f, indent=4)

# --- 10. Summary info ---
print(f"✅ Plane mesh saved to: {plane_filename}")
print(f"✅ Buildings mesh saved to: {buildings_filename}")
print(f"📄 Metadata saved: {sample_id}_metadata.json")
print(f"🏙 Buildings: {len(cylinders)} | Rotation: {angle_deg:.2f}°")

# --- 11. Generate "geometry.toml" ---
def generate_geometry_toml(x: int, output_file: str = "geometry.toml"):
    # Fixed STL filenames except the two dynamic ones
    filenames = {
        0: "./stl/inlet.stl",
        1: "./stl/outlet.stl",
        2: "./stl/wall_left.stl",
        3: "./stl/wall_right.stl",
        4: "./stl/wall_top.stl",
        5: "./stl/wall_bottom_front.stl",
        6: "./stl/wall_bottom_back.stl",
        7: f"./stl/wall_bottom_center_{x}.stl",
        8: f"./stl/buildings_{x}.stl"
    }

    # Boundary conditions
    bc = {
        0: 1000,
        1: 4000,
        2: 3020,
        3: 3020,
        4: 3020,
        5: 3020,
        6: 3020,
        7: 2000,
        8: 2000
    }

    # Segment name to index mapping
    body_segments = {
        "body_segments.inlet": 0,
        "body_segments.outlet": 1,
        "body_segments.left": 2,
        "body_segments.right": 3,
        "body_segments.top": 4,
        "body_segments.bottom_front": 5,
        "body_segments.bottom_back": 6,
        "body_segments.bottom_center": 7,
        "body_segments.buildings": 8
    }

    # Assemble dictionary for TOML
    geometry = {
        "noSegments": 9,
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

    print(f"✅ geometry.toml generated (x = {x})")

generate_geometry_toml(x=sample_id)
