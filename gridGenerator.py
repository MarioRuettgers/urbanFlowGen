import toml
import json
import sys
import os

#--- User input ---
if len(sys.argv) < 2:
    raise ValueError("Missing required argument: sample_id")
sample_id = int(sys.argv[1])  # USER-DEFINED SAMPLE ID
json_path = os.path.join('.', str(sample_id), 'stl', f'{sample_id}_metadata.json')

# Load building data
def load_building_data(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    positions = data["building_positions"]
    sizes = data["building_sizes"]
    heights = data["building_heights"]

    buildings = []
    for pos, size, height in zip(positions, sizes, heights):
        building = (tuple(pos), tuple(size), height)
        buildings.append(building)

    return buildings

# Load user config
config = toml.load('config.toml')

# Extract grid and geometry parameters
refine = config['grid_mAIA']
refine_global = config['global']
refine_plate = config['bottom_center']

# Unpack basic settings
reductionFactor = refine['RF']
minLevel = refine['RL_min']
maxUniformRefinementLevel = refine['RL_max_unif']
maxRfnmntLvl = refine['RL_max']
maxBoundaryRfnLvl = refine['RL_max']

x_incr = refine['x_incr']
y_incr = refine['y_incr']
z_incr = refine['z_incr']
boundary_ref = refine['REF_b']
wake_ref_x = refine['REF_w']

x_min = refine_global['x_min']
x_max = refine_global['x_max']
z_min = refine_global['z_min']
L = x_max - x_min

x0, x1 = refine_plate['x_min_VII'], refine_plate['x_max_VII']
y0, y1 = refine_plate['y_min_VII'], refine_plate['y_max_VII']

def cell_size(level, RF, L):
    return (RF * L) / (2 ** level)

# Load buildings
buildings = load_building_data(json_path)

# --- Patch logic ---

# Dictionary to hold patches for each refinement level
refinement_by_level = {}

# === BUILDING REFINEMENT PATCHES ===
for pos, (w, h), height in buildings:
    cx, cy = pos
    xmin = xmax = ymin = ymax = zmin = zmax = None  # Initialize

    for level in range(maxRfnmntLvl, minLevel, -1):
        cs = cell_size(level, reductionFactor, L)

        if level == maxRfnmntLvl:
            # Finest level: base box
            dx_neg = dx_pos = boundary_ref * cs
            dy_neg = dy_pos = boundary_ref * cs
            dz = boundary_ref * cs

            xmin = cx - w / 2 - dx_neg
            xmax = cx + w / 2 + dx_pos
            ymin = cy - h / 2 - dy_neg
            ymax = cy + h / 2 + dy_pos
            zmin = z_min
            zmax = z_min + height + dz

        elif level == maxRfnmntLvl - 1:
            # Wake refinement: asymmetric in x
            dx_neg = x_incr * cs
            dx_pos = wake_ref_x * cs
            dy_neg = dy_pos = y_incr * cs
            dz = z_incr * cs

            xmin -= dx_neg
            xmax += dx_pos
            ymin -= dy_neg
            ymax += dy_pos
            zmax += dz

        else:
            # Symmetric expansion
            dx = x_incr * cs
            dy = y_incr * cs
            dz = z_incr * cs

            xmin -= dx
            xmax += dx
            ymin -= dy
            ymax += dy
            zmax += dz

        refinement_by_level.setdefault(level, []).append({
            'type': 'building',
            'level': level,
            'xmin': xmin,
            'xmax': xmax,
            'ymin': ymin,
            'ymax': ymax,
            'zmin': zmin,
            'zmax': zmax
        })

# === FLOOR REFINEMENT PATCHES ===
xmin, xmax = x0, x1
ymin, ymax = y0, y1
zmin = z_min
zmax = z_min  # Floor stays at zmin

for level in range(maxRfnmntLvl, minLevel, -1):
    cs = cell_size(level, reductionFactor, L)

    dx = x_incr * cs
    dy = y_incr * cs
    dz = z_incr * cs

    xmin -= dx
    xmax += dx
    ymin -= dy
    ymax += dy
    zmax += dz

    # Append patch directly
    refinement_by_level.setdefault(level, []).append({
        'type': 'floor',
        'level': level,
        'xmin': xmin,
        'xmax': xmax,
        'ymin': ymin,
        'ymax': ymax,
        'zmin': zmin,
        'zmax': zmax
    })

# === Convert to TOML-compatible fields ===
methods = []
properties = []

for level in range(maxRfnmntLvl, minLevel - 1, -1):
    boxes = refinement_by_level.get(level, [])
    methods.append('B' * len(boxes))
    for box in boxes:
        properties.extend([
            box['xmin'], box['ymin'], box['zmin'],
            box['xmax'], box['ymax'], box['zmax']
        ])

# === Assemble full properties dict ===
properties_dict = {
    'gridGenerator': True,
    'flowSolver': False,
    'nDim': 3,
    'noSolvers': 2,
    'scratchSize': 20.0,

    'outputDir': 'out/',
    'gridInputFileName': 'grid.Netcdf',
    'gridOutputFileName': 'grid.Netcdf',

    'multiSolverGrid': True,
    'multiSolver': True,
    'noHaloLayers': 1,

    'reductionFactor': reductionFactor,
    'minLevel': minLevel,
    'maxUniformRefinementLevel': maxUniformRefinementLevel,
    'maxRfnmntLvl': maxRfnmntLvl,
    'maxBoundaryRfnLvl': maxBoundaryRfnLvl,
    'localRfnMethod': 1,
    'maxNoCells': 300_000_000,
    'partitionCellOffspringThreshold': 50_000_000,

    'localRfnLvlMethods': '-'.join(methods).rstrip('-'),
    'solver': {
        '0': {'geometryInputFileName': 'geometry.toml'},
        '1': {'geometryInputFileName': 'geometry.toml'}
    }
}

# === Reverse properties list grouped by box (6 values per box) ===
chunk_size = 6
property_chunks = [properties[i:i+chunk_size] for i in range(0, len(properties), chunk_size)]
property_chunks.reverse()
properties = [value for chunk in property_chunks for value in chunk]

# === Write to TOML file ===
toml_str = toml.dumps(properties_dict)

# Format localRfnLevelProperties manually for readability
formatted_properties_lines = []
for i in range(0, len(properties), 6):
    group = properties[i:i+6]
    line = "  " + ", ".join(f"{v:.6f}" for v in group) + ","  # trailing comma for readability
    formatted_properties_lines.append(line)

formatted_properties = "localRfnLevelProperties = [\n" + "\n".join(formatted_properties_lines) + "\n]\n"

# Insert formatted_properties before the solver blocks
insertion_point = toml_str.find("[solver.0]")
toml_str = toml_str[:insertion_point] + formatted_properties + "\n" + toml_str[insertion_point:]

# Final cleanup (e.g., avoid ",\n]" if it appears somewhere)
toml_str = toml_str.replace(',\n]', '\n]')

with open("properties_grid.toml", "w") as f:
    f.write(toml_str)


