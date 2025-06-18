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

# Parts of the geometry
# Inlet - I
# Outlet - II
# Wall left - III
# Wall right - IV
# Wall top - V
# Wall bottom front (slip) - VI
# Wall bottom back (slip) - VII
# Wall bottom center (no-slip) - VIII

#--- User input ---
if len(sys.argv) < 2:
    raise ValueError("Missing required argument: sample_id")
sample_id = int(sys.argv[1])  # USER-DEFINED SAMPLE ID

# --- Parameters ---
x_min, x_max=-850,850 # Global x range 
y_min, y_max = -350, 350 # Global y range
z_min, z_max = -350, 350 # Global z range

x_min_VIII, x_max_VIII = -300, 300 # x range for wall bottom center - VIII

# Safety distances
margin_x = 100 # Minimum distance to wall bottom front (slip) - VI (after rotation)
margin_y = 150 # Minimum distance to wall left - III, and wall right - IV (after rotation)
min_building_distance = 5  # Minimum distance between building surfaces

# Normal buildings
min_size, max_size = 10, 80 # Range of normal building edge length
normal_aspect_ratio = 2.5 # Maximum aspect ratio for normal buildings

# Extreme buildings
extreme_chance = 0.15 # Probability for extreme building
extreme_aspect_ratio = 5.0 # Maximum aspect ratio for extreme buildings

# Circular buildings
circle_chance = 0.05 # Probability for circular building
circle_resolution = 32 # Circumferential resolution

# Height for normal, extreme, and circular building
min_height, max_height = 5, 80 

# Towers
tower_chance = 0.07 # Probability for tower
tower_min_size, tower_max_size = 50, 100 # Range of tower edge length
tower_min_height, tower_max_height = 80, 200 # Range of tower height
tower_max_aspect_ratio = 1.5 # Maximum aspect ratio for towers

# Roads
road_width = 10 # Road size

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
plane.export('inlet.stl', file_type='stl_ascii')

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
plane.export('outlet.stl', file_type='stl_ascii')

######################################
# Wall left - III 
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
plane.export('wall_left.stl', file_type='stl_ascii')

######################################
# Wall right - IV
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
plane.export('wall_right.stl', file_type='stl_ascii')

######################################
# Wall top - V
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
plane.export('wall_top.stl', file_type='stl_ascii')

######################################
# Wall bottom front (slip) - VI
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
plane.export('wall_bottom_front.stl', file_type='stl_ascii')

######################################
# Wall bottom back (slip) - VII
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
plane.export('wall_bottom_back.stl', file_type='stl_ascii')

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
def generate_random_roads(x_min_VIII, x_max_VIII, y_min, y_max, road_width):
    global num_vertical_roads, num_horizontal_roads
    num_vertical_roads = np.random.randint(3, 8)
    num_horizontal_roads = np.random.randint(3, 8)

    vertical_positions = np.sort(np.random.uniform(x_min_VIII + margin_x, x_max_VIII - margin_x, num_vertical_roads))
    horizontal_positions = np.sort(np.random.uniform(y_min + margin_y, y_max - margin_y, num_horizontal_roads))

    vertical_roads = [
        LineString([[x, y_min], [x, y_max]]).buffer(road_width / 2)
        for x in vertical_positions
    ]
    horizontal_roads = [
        LineString([[x_min_VIII, y], [x_max_VIII, y]]).buffer(road_width / 2)
        for y in horizontal_positions
    ]

    return vertical_roads + horizontal_roads

roads = generate_random_roads(x_min_VIII, x_max_VIII, y_min, y_max, road_width)
rotated_roads = [rotate(road, angle_deg, origin=(0, 0)) for road in roads]
road_union = unary_union(rotated_roads)

# --- 4. Generate building footprints ---
def random_building_footprint():
    shape = 'rect'
    if np.random.rand() < circle_chance:
        diameter = np.random.uniform(min_size, max_size)
        height = np.random.uniform(min_height, max_height)
        shape = 'circle'
        return diameter, diameter, height, shape

    if np.random.rand() < tower_chance:
        for _ in range(100):
            w = np.random.uniform(tower_min_size, tower_max_size)
            h = np.random.uniform(tower_min_size, tower_max_size)
            if max(w / h, h / w) <= tower_max_aspect_ratio:
                height = np.random.uniform(tower_min_height, tower_max_height)
                return w, h, height, shape
    else:
        for _ in range(100):
            w = np.random.uniform(min_size, max_size)
            h = np.random.uniform(min_size, max_size)
            aspect = max(w / h, h / w)
            limit = extreme_aspect_ratio if np.random.rand() < extreme_chance else normal_aspect_ratio
            if aspect <= limit:
                height = np.random.uniform(min_height, max_height)
                return w, h, height, shape
    raise ValueError("Couldn't generate a valid building footprint.")

# --- 5. Generate buildings ---
num_buildings = np.random.randint(2, 13)
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
    buffer_x = margin_x + diag / 2
    buffer_y = margin_y + diag / 2

    x_range = (x_min_VIII + buffer_x, x_max_VIII - buffer_x)
    y_range = (y_min + buffer_y, y_max - buffer_y)

    initial_pos = np.array([
        np.random.uniform(*x_range),
        np.random.uniform(*y_range)
    ])
    rotated_pos = initial_pos @ R.T

    if shape == 'circle':
        radius = w / 2
        theta = np.linspace(0, 2 * np.pi, circle_resolution, endpoint=False)
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
    
    buffered_hole = hole_poly.buffer(min_building_distance)
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
        building = trimesh.creation.cylinder(radius=radius, height=height, sections=circle_resolution)
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
filename = f'{sample_id}.stl'
with open(filename, 'w') as f:
    f.write(trimesh.exchange.stl.export_stl_ascii(trimesh.util.concatenate([surface_mesh] + cylinders)))

# --- 9. Save metadata to JSON ---
metadata = {
    "sample_id": sample_id,
    "rotation_angle_deg": round(angle_deg, 2),
    "domain": {"x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max},
    "wall bottom center (no-slip) - VIII": {"x_min_VIII": x_min_VIII, "x_max_VIII": x_max_VIII},
    "margin_x": margin_x,
    "margin_y": margin_y,
    "building_count": len(cylinders),
    "circle_chance": circle_chance,
    "tower_chance": tower_chance,
    "extreme_aspect_chance": extreme_chance,
    "aspect_ratio_limits": {
        "normal_max": normal_aspect_ratio,
        "extreme_max": extreme_aspect_ratio
    },
    "building_size_range": [min_size, max_size],
    "building_height_range": [min_height, max_height],
    "tower_size_range": [tower_min_size, tower_max_size],
    "tower_height_range": [tower_min_height, tower_max_height],
    "tower_max_aspect_ratio": tower_max_aspect_ratio,
    "circle_resolution": circle_resolution,
    "road_width": road_width,
    "vertical_road_count": num_vertical_roads,
    "horizontal_road_count": num_horizontal_roads,
    "building_shapes": shapes,
    "building_sizes": sizes,
    "building_heights": heights,
    "min_building_distance": min_building_distance
}

with open(f'{sample_id}_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=4)

# --- 10. Summary info ---
print(f"✅ Exported: {filename}")
print(f"📄 Metadata saved: {sample_id}_metadata.json")
print(f"🏙 Buildings: {len(cylinders)} | Rotation: {angle_deg:.2f}°")

