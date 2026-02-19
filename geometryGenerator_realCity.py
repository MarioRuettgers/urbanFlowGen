"""
realCityGeometryGenerator.py
Real city geometry generator for urbanFlowGen CFD simulations

This script generates CFD geometries using real city building data from Overture Maps.
Buildings are sampled from actual urban areas and scaled to fit the CFD domain.
"""

import trimesh
import numpy as np
import json
import sys
import os
import toml

# Required for Overture Maps data
try:
    import overturemaps
    from shapely import from_wkb
    from shapely.geometry import Point, Polygon
    from shapely.ops import transform
    import pyproj
except ImportError as e:
    print(f" Error: Missing required packages. Please install:")
    print(" pip install overturemaps pyproj shapely")
    sys.exit(1)

# Optional: GeoDataFrame support (more stable)
try:
    import geopandas as gpd
    import pandas as pd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    print(" Warning: geopandas not available. Using simple mode only.")

# Optional: WFS support for Global Building Atlas
try:
    from owslib.wfs import WebFeatureService
    import requests
    WFS_AVAILABLE = True
except ImportError:
    WFS_AVAILABLE = False
    print(" Warning: owslib not available. Global Building Atlas mode disabled.")

# ========================================
# CONFIGURATION LOADING
# ========================================
city_config = toml.load('config_realCity.toml')
cfd_config = toml.load('config.toml')

# User input - support both old and new formats
# Old format: python script.py sample_id
# New format: python script.py sample_id --lat 37.5 --lon 127.0 --utm-zone 52
import argparse

parser = argparse.ArgumentParser(description='Real City Geometry Generator')
parser.add_argument('sample_id', type=int, help='Sample ID number')
parser.add_argument('--lat', '--latitude', type=float, default=None,
                    help='Exact latitude (overrides config)')
parser.add_argument('--lon', '--longitude', type=float, default=None,
                    help='Exact longitude (overrides config)')
parser.add_argument('--utm-zone', type=int, default=None,
                    help='UTM zone (optional, auto-calculated from longitude if not provided)')

args = parser.parse_args()
sample_id = args.sample_id

stl_path = os.path.join('.', str(sample_id), 'stl')
geometry_path = os.path.join('.', str(sample_id))
os.makedirs(stl_path, exist_ok=True)

# Extract CFD domain parameters
x_min = cfd_config['global']['x_min']
x_max = cfd_config['global']['x_max']
y_min = cfd_config['global']['y_min']
y_max = cfd_config['global']['y_max']
z_min = cfd_config['global']['z_min']
z_max = cfd_config['global']['z_max']

x_min_VII = cfd_config['bottom_center']['x_min_VII']
x_max_VII = cfd_config['bottom_center']['x_max_VII']
y_min_VII = cfd_config['bottom_center']['y_min_VII']
y_max_VII = cfd_config['bottom_center']['y_max_VII']


# ========================================
# PART A: CFD DOMAIN WALL GENERATION
# (Copied from geometryGenerator.py)
# ========================================

def make_patch(v0, v1, v2, v3):
    """Create a rectangular patch mesh from four corner vertices."""
    vertices = np.array([v0, v1, v2, v3])
    faces = np.array([[0, 1, 2], [0, 2, 3]])
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)


def create_cfd_walls():
    """Generate CFD domain walls (inlet, outlet, top, sides, bottom)"""
    print("🏗️  Generating CFD domain walls...")
    
    # Inlet - I
    inlet = make_patch(
        [x_min, y_min, z_min],
        [x_min, y_max, z_min],
        [x_min, y_max, z_max],
        [x_min, y_min, z_max]
    )
    inlet.export(os.path.join(stl_path, 'inlet.stl'), file_type='stl_ascii')
    
    # Outlet - II
    outlet = make_patch(
        [x_max, y_min, z_min],
        [x_max, y_max, z_min],
        [x_max, y_max, z_max],
        [x_max, y_min, z_max]
    )
    outlet.export(os.path.join(stl_path, 'outlet.stl'), file_type='stl_ascii')
    
    # Left - III
    left = make_patch(
        [x_min, y_max, z_min],
        [x_max, y_max, z_min],
        [x_max, y_max, z_max],
        [x_min, y_max, z_max]
    )
    left.export(os.path.join(stl_path, 'left.stl'), file_type='stl_ascii')
    
    # Right - IV
    right = make_patch(
        [x_min, y_min, z_min],
        [x_max, y_min, z_min],
        [x_max, y_min, z_max],
        [x_min, y_min, z_max]
    )
    right.export(os.path.join(stl_path, 'right.stl'), file_type='stl_ascii')
    
    # Top - V
    top = make_patch(
        [x_min, y_min, z_max],
        [x_max, y_min, z_max],
        [x_max, y_max, z_max],
        [x_min, y_max, z_max]
    )
    top.export(os.path.join(stl_path, 'top.stl'), file_type='stl_ascii')
    
    # Bottom around plate - VI
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
    
    print("   ✅ CFD walls created (inlet, outlet, left, right, top, bottom_around_plate)")


# ========================================
# PART B: REAL CITY BUILDING DATA COLLECTION
# ========================================

def calculate_utm_zone(longitude):
    """Calculate UTM zone from longitude"""
    return int((longitude + 180) / 6) + 1


def sample_location_in_city(force_lat=None, force_lon=None, force_utm_zone=None):
    """
    Sample location - supports three modes:
    1. Command-line exact coordinates (--lat --lon, --utm-zone optional)
    2. Config file exact coordinates (use_exact_location = true)
    3. Random sampling within city radius (default)

    Args:
        force_lat: Override latitude from command line
        force_lon: Override longitude from command line
        force_utm_zone: Override UTM zone from command line (optional, auto-calculated if None)

    Returns:
        (latitude, longitude, city_name, utm_zone)
    """
    # Priority 1: Command-line arguments
    if force_lat is not None and force_lon is not None:
        # Auto-calculate UTM zone if not provided
        if force_utm_zone is None:
            force_utm_zone = calculate_utm_zone(force_lon)
            print(f" Using exact coordinates from command line")
            print(f" Lat: {force_lat}, Lon: {force_lon}")
            print(f" UTM Zone auto-calculated: {force_utm_zone}")
        else:
            print(f" Using exact coordinates from command line")
            print(f" Lat: {force_lat}, Lon: {force_lon}, UTM Zone: {force_utm_zone}")
        return force_lat, force_lon, "CommandLine_Custom", force_utm_zone

    # Priority 2: Config file exact location
    use_exact = city_config['settings'].get('use_exact_location', False)
    if use_exact:
        exact_config = city_config.get('exact_location', {})
        exact_lat = exact_config.get('latitude')
        exact_lon = exact_config.get('longitude')
        exact_utm = exact_config.get('utm_zone')
        exact_desc = exact_config.get('description', 'Custom')

        if exact_lat is None or exact_lon is None:
            raise ValueError("use_exact_location=true but latitude/longitude missing in exact_location section")

        # Auto-calculate UTM zone if not provided
        if exact_utm is None:
            exact_utm = calculate_utm_zone(exact_lon)
            print(f" Using exact coordinates from config file")
            print(f" Lat: {exact_lat}, Lon: {exact_lon}")
            print(f" UTM Zone auto-calculated: {exact_utm}")
            print(f" Description: {exact_desc}")
        else:
            print(f" Using exact coordinates from config file")
            print(f" Lat: {exact_lat}, Lon: {exact_lon}, UTM Zone: {exact_utm}")
            print(f" Description: {exact_desc}")

        return exact_lat, exact_lon, f"Config_{exact_desc}", exact_utm

    # Priority 3: Random sampling (original behavior)
    # Get list of active cities
    active_cities = city_config['settings']['active_cities']

    # Randomly select one city from the list
    city_name = np.random.choice(active_cities)
    city = city_config['cities'][city_name]

    print(f" Random sampling mode")
    print(f" Selected from pool: {', '.join(active_cities)}")

    # Uniform distribution in circle using polar coordinates
    r = np.sqrt(np.random.random()) * city['sampling_radius_km'] * 1000  # meters
    theta = np.random.random() * 2 * np.pi

    # Convert to lat/lon offset (simple approximation)
    meter_per_degree_lat = 111320
    meter_per_degree_lon = 111320 * np.cos(np.radians(city['center_lat']))

    delta_lat = (r * np.cos(theta)) / meter_per_degree_lat
    delta_lon = (r * np.sin(theta)) / meter_per_degree_lon

    sampled_lat = city['center_lat'] + delta_lat
    sampled_lon = city['center_lon'] + delta_lon

    return sampled_lat, sampled_lon, city_name, city['utm_zone']


def calculate_bbox_for_circle(lat, lon, radius_m):
    """Calculate bounding box that contains a circle"""
    # Simple approximation
    meter_per_degree_lat = 111320
    meter_per_degree_lon = 111320 * np.cos(np.radians(lat))
    
    delta_lat = radius_m / meter_per_degree_lat
    delta_lon = radius_m / meter_per_degree_lon
    
    bbox = (
        lon - delta_lon * 1.5,  # Add buffer for safety
        lat - delta_lat * 1.5,
        lon + delta_lon * 1.5,
        lat + delta_lat * 1.5
    )
    
    return bbox


def fetch_buildings_simple(bbox, utm_zone):
    """Fetch buildings using simple Overture Maps approach"""
    print("   📡 Fetching building data (simple mode)...")
    
    try:
        table = overturemaps.record_batch_reader("building", bbox).read_all()
        data = table.to_pylist()
    except Exception as e:
        print(f" Failed to fetch data: {e}")
        return None
    
    if not data:
        print(" No buildings found in this area")
        return None
    
    print(f" Fetched {len(data)} buildings")
    
    # Convert to simple list of dicts with geometry and height
    buildings = []
    for record in data:
        try:
            geom = from_wkb(record['geometry'])
            height = record.get('height')
            
            # Skip if no height and default_height is 0
            if (height is None or height == 0) and city_config['settings']['default_height'] == 0:
                continue
            
            if height is None or height == 0:
                height = city_config['settings']['default_height']
            
            buildings.append({
                'geometry': geom,
                'height': float(height)
            })
        except Exception:
            continue
    
    return buildings


def fetch_buildings_geopandas(bbox, utm_zone):
    """Fetch buildings using GeoDataFrame approach (more stable)"""
    if not GEOPANDAS_AVAILABLE:
        raise ImportError("geopandas required for this mode")

    print(" Fetching building data (geopandas mode)...")

    try:
        table = overturemaps.record_batch_reader("building", bbox).read_all()
        data = table.to_pylist()
    except Exception as e:
        print(f" Failed to fetch data: {e}")
        return None

    if not data:
        print(" No buildings found in this area")
        return None

    print(f" Fetched {len(data)} raw buildings")

    # DEBUG: Check first building's fields
    if len(data) > 0:
        print(f" DEBUG - First building fields: {list(data[0].keys())}")
        sample = data[0]
        print(f" DEBUG - Sample values:")
        for key in ['height', 'num_floors', 'level', 'min_height', 'roof_height']:
            if key in sample:
                print(f"      {key}: {sample[key]}")

    # Convert to GeoDataFrame and analyze height data
    geoms = []
    heights = []
    heights_with_data = 0
    heights_missing = 0

    for r in data:
        geoms.append(from_wkb(r['geometry']))
        h = r.get('height')

        if h is not None and h > 0:
            heights.append(float(h))
            heights_with_data += 1
        else:
            heights.append(city_config['settings']['default_height'])
            heights_missing += 1

    print(f" Height data: {heights_with_data} with real heights, {heights_missing} using default ({city_config['settings']['default_height']}m)")

    if heights_with_data > 0:
        real_heights = [h for h in heights if h != city_config['settings']['default_height']]
        print(f" Height range: {min(real_heights):.1f}m - {max(real_heights):.1f}m (avg: {sum(real_heights)/len(real_heights):.1f}m)")

    gdf = gpd.GeoDataFrame({'height': heights}, geometry=geoms, crs="EPSG:4326")

    # Convert to UTM
    epsg = f"EPSG:326{utm_zone}" if utm_zone > 0 else f"EPSG:327{abs(utm_zone)}"
    gdf_utm = gdf.to_crs(epsg)

    # Explode MultiPolygons
    gdf_utm = gdf_utm.explode(index_parts=False).reset_index(drop=True)

    # Filter out buildings with no height if default_height is 0
    if city_config['settings']['default_height'] == 0:
        gdf_utm = gdf_utm[gdf_utm['height'] > 0]

    print(f" Processed {len(gdf_utm)} valid buildings")

    return gdf_utm


def fetch_buildings_wfs(bbox, utm_zone):
    """Fetch buildings from Global Building Atlas via WFS (only requested area, not full dataset)"""
    if not WFS_AVAILABLE or not GEOPANDAS_AVAILABLE:
        raise ImportError("owslib and geopandas required for WFS mode")

    print(" Fetching building data from Global Building Atlas (WFS)...")
    print(" Note: Only downloading data for requested bbox area (not entire dataset)")

    # Get WFS configuration
    wfs_config = city_config.get('global_building_atlas', {})
    wfs_url = wfs_config.get('wfs_url', 'https://tubvsig-so2sat-vm1.srv.mwn.de/geoserver/ows')
    layer_name = wfs_config.get('layer_name', 'gba:GBA_Polygon')
    height_field = wfs_config.get('height_field', 'height')
    wfs_crs = wfs_config.get('crs', 'EPSG:3857')  # GBA uses EPSG:3857

    try:
        # Method 1: Try using OWSLib (more robust for WFS)
        print(" Attempting WFS connection via OWSLib...")

        try:
            wfs = WebFeatureService(wfs_url, version='2.0.0', timeout=30)
            print(f" WFS server connected")
            print(f" Available layers: {list(wfs.contents.keys())[:5]}...")  # Show first 5 layers

            # Check if layer exists
            if layer_name not in wfs.contents:
                print(f" Layer '{layer_name}' not found. Trying alternative layer names...")
                # Try common alternatives
                alternatives = [k for k in wfs.contents.keys() if 'polygon' in k.lower() or 'building' in k.lower()]
                if alternatives:
                    layer_name = alternatives[0]
                    print(f" Using layer: {layer_name}")
                else:
                    raise ValueError(f"No suitable layer found. Available: {list(wfs.contents.keys())}")

        except Exception as e:
            print(f" OWSLib connection failed: {e}")
            print(f" Falling back to direct HTTP request...")

        # Convert WGS84 bbox to EPSG:3857 if needed
        # bbox is in WGS84 (lon_min, lat_min, lon_max, lat_max)
        if wfs_crs == 'EPSG:3857':
            # Transform bbox to EPSG:3857
            from shapely.geometry import box as shapely_box
            from shapely.ops import transform

            project = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform
            bbox_geom = shapely_box(bbox[0], bbox[1], bbox[2], bbox[3])
            bbox_3857 = transform(project, bbox_geom)
            bbox_tuple = bbox_3857.bounds
            bbox_str = f"{bbox_tuple[0]},{bbox_tuple[1]},{bbox_tuple[2]},{bbox_tuple[3]},EPSG:3857"
        else:
            bbox_tuple = bbox
            bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]},EPSG:4326"

        print(f" WFS URL: {wfs_url}")
        print(f" Layer: {layer_name}")
        print(f" BBOX: {bbox_str}")

        # Build WFS GetFeature request (fetches only data within bbox)
        params = {
            'service': 'WFS',
            'version': '2.0.0',
            'request': 'GetFeature',
            'typeName': layer_name,
            'bbox': bbox_str,
            'outputFormat': 'application/json',
            'srsName': wfs_crs,
            'maxFeatures': 10000  # Limit to prevent server overload
        }

        # Use GeoPandas to read WFS directly
        from urllib.parse import urlencode
        full_url = f"{wfs_url}?{urlencode(params)}"

        print(f" Sending WFS GetFeature request...")

        # Read GeoJSON from WFS (only downloads bbox area!)
        import time
        start_time = time.time()
        gdf = gpd.read_file(full_url)
        elapsed = time.time() - start_time

        print(f" Download completed in {elapsed:.2f}s")

        if gdf.empty:
            print(" No buildings found in this area")
            return None

        print(f" Fetched {len(gdf)} raw buildings from WFS")

        # Extract height field (field name may vary)
        if height_field not in gdf.columns:
            # Try common alternatives
            possible_fields = ['height', 'height_m', 'bld_height', 'h_mean', 'HEIGHT']
            height_field = next((f for f in possible_fields if f in gdf.columns), None)

            if height_field is None:
                print(f" No height field found. Available fields: {list(gdf.columns)}")
                print(f" Using default height: {city_config['settings']['default_height']}m")
                gdf['height'] = city_config['settings']['default_height']
            else:
                print(f" Using height field: {height_field}")
                gdf['height'] = gdf[height_field]
        else:
            gdf['height'] = gdf[height_field]

        # Fill missing heights with default
        gdf['height'] = gdf['height'].fillna(city_config['settings']['default_height'])

        # Convert to UTM
        epsg = f"EPSG:326{utm_zone}" if utm_zone > 0 else f"EPSG:327{abs(utm_zone)}"
        gdf_utm = gdf.to_crs(epsg)

        # Explode MultiPolygons
        gdf_utm = gdf_utm.explode(index_parts=False).reset_index(drop=True)

        # Filter out buildings with no height if default_height is 0
        if city_config['settings']['default_height'] == 0:
            gdf_utm = gdf_utm[gdf_utm['height'] > 0]

        # Keep only geometry and height columns
        gdf_utm = gdf_utm[['geometry', 'height']]

        print(f" Processed {len(gdf_utm)} valid buildings from Global Building Atlas")

        return gdf_utm

    except Exception as e:
        print(f" WFS request failed: {e}")
        print(f" This may be due to:")
        print(f"       - Server is down or unreachable")
        print(f"       - Incorrect layer name (check with GetCapabilities)")
        print(f"       - BBOX outside data coverage area")
        return None


def filter_circular_buildings(buildings_data, center_lat, center_lon, radius_m, utm_zone):
    """Filter buildings within circular domain"""
    print(f" Filtering buildings within {radius_m}m radius...")

    # Project center to UTM
    epsg = f"EPSG:326{utm_zone}" if utm_zone > 0 else f"EPSG:327{abs(utm_zone)}"
    project = pyproj.Transformer.from_crs("EPSG:4326", epsg, always_xy=True).transform
    center_utm = project(center_lon, center_lat)
    center_point = Point(center_utm)

    print(f" Center UTM: {center_utm}")
    print(f" UTM Zone: {epsg}")

    if isinstance(buildings_data, gpd.GeoDataFrame):
        # GeoDataFrame mode
        print(f" Buildings CRS: {buildings_data.crs}")
        buildings_data['distance'] = buildings_data.geometry.centroid.distance(center_point)
        print(f" Distance range: {buildings_data['distance'].min():.2f}m - {buildings_data['distance'].max():.2f}m")
        print(f" Radius threshold: {radius_m}m")
        filtered = buildings_data[buildings_data['distance'] <= radius_m].copy()
        filtered = filtered.drop(columns=['distance'])
    else:
        # Simple mode - convert to UTM and filter
        project_geom = lambda geom: transform(project, geom)
        filtered = []
        for bldg in buildings_data:
            geom_utm = project_geom(bldg['geometry'])
            centroid = geom_utm.centroid
            distance = center_point.distance(centroid)
            
            if distance <= radius_m:
                filtered.append({
                    'geometry': geom_utm,
                    'height': bldg['height']
                })
    
    count = len(filtered)
    print(f" {count} buildings within circular domain")
    
    if count == 0:
        return None
    
    return filtered, center_utm


# ========================================
# PART C: 3D MESH GENERATION
# ========================================

def transform_to_section_vii(buildings_data, center_utm):
    """Transform real city buildings to fit CFD section VII with safety margins"""
    print(" Transforming buildings to section VII with safety margins...")
    
    # Load safety distances from config.toml
    sd_x_neg = cfd_config['safety']['sd_x_neg']
    sd_x_pos = cfd_config['safety']['sd_x_pos']
    sd_y = cfd_config['safety']['sd_y']
    
    # Calculate section VII size
    section_vii_width = x_max_VII - x_min_VII
    section_vii_height = y_max_VII - y_min_VII
    
    # Calculate safe zone dimensions (subtract safety margins)
    safe_width = section_vii_width - sd_x_neg - sd_x_pos
    safe_height = section_vii_height - 2 * sd_y
    safe_zone_diameter = min(safe_width, safe_height)
    
    # Calculate scale factor based on safe zone
    collection_diameter = city_config['settings']['collection_radius_meters'] * 2
    scale_factor = safe_zone_diameter / collection_diameter
    
    # Calculate safe zone center (offset from section VII due to asymmetric safety margins)
    safe_zone_center = (
        x_min_VII + sd_x_neg + safe_width / 2,
        y_min_VII + sd_y + safe_height / 2
    )
    
    print(f" Section VII size: {section_vii_width} × {section_vii_height}")
    print(f" Safety margins: X=({sd_x_neg}, {sd_x_pos}), Y={sd_y}")
    print(f" Safe zone size: {safe_width} × {safe_height}")
    print(f" Collection diameter: {collection_diameter}m")
    print(f" Scale factor: {scale_factor:.4f} (1:{1/scale_factor:.1f})")
    print(f" Buildings will be scaled: XY and Z (height) both scaled by {scale_factor:.4f}")
    
    if isinstance(buildings_data, gpd.GeoDataFrame):
        # GeoDataFrame mode
        transformed = buildings_data.copy()
        transformed.geometry = transformed.translate(
            xoff=-center_utm[0],
            yoff=-center_utm[1]
        ).scale(
            xfact=scale_factor,
            yfact=scale_factor,
            origin=(0, 0)
        ).translate(
            xoff=safe_zone_center[0],
            yoff=safe_zone_center[1]
        )
        # CRITICAL: Scale height by the same factor to maintain proportions
        transformed['height'] = transformed['height'] * scale_factor
    else:
        # Simple mode
        transformed = []
        for bldg in buildings_data:
            geom = bldg['geometry']

            # Translate to origin
            from shapely.affinity import translate, scale as shapely_scale
            geom = translate(geom, xoff=-center_utm[0], yoff=-center_utm[1])

            # Scale
            geom = shapely_scale(geom, xfact=scale_factor, yfact=scale_factor, origin=(0, 0))

            # Translate to safe zone center
            geom = translate(geom, xoff=safe_zone_center[0], yoff=safe_zone_center[1])

            # CRITICAL: Scale height by the same factor to maintain proportions
            transformed.append({
                'geometry': geom,
                'height': bldg['height'] * scale_factor
            })
    
    return transformed, safe_zone_center


def apply_rotation(buildings_data, safe_zone_center):
    """Apply random rotation (0-90 degrees) around safe zone center"""
    angle_deg = np.random.uniform(0, 90)
    print(f" Applying rotation: {angle_deg:.2f}°")
    
    if isinstance(buildings_data, gpd.GeoDataFrame):
        # GeoDataFrame mode
        rotated = buildings_data.copy()
        rotated.geometry = rotated.rotate(angle_deg, origin=safe_zone_center)
    else:
        # Simple mode
        from shapely.affinity import rotate
        rotated = []
        for bldg in buildings_data:
            geom = rotate(bldg['geometry'], angle_deg, origin=safe_zone_center)
            rotated.append({
                'geometry': geom,
                'height': bldg['height']
            })
    
    return rotated, angle_deg


def extract_building_footprints(buildings_data):
    """Extract 2D building footprints as Polygon list for bottom plate holes"""
    footprints = []
    
    if isinstance(buildings_data, gpd.GeoDataFrame):
        # GeoDataFrame mode
        for idx, row in buildings_data.iterrows():
            geom = row.geometry
            
            # Skip invalid geometries
            if geom.is_empty or not geom.is_valid:
                continue
            
            # Handle Polygon
            if isinstance(geom, Polygon):
                footprints.append(geom)
            
            # Handle MultiPolygon (explode)
            elif hasattr(geom, 'geoms'):
                for poly in geom.geoms:
                    if isinstance(poly, Polygon) and poly.is_valid:
                        footprints.append(poly)
    else:
        # Simple mode
        for bldg in buildings_data:
            geom = bldg['geometry']
            
            if geom.is_empty or not geom.is_valid:
                continue
            
            if isinstance(geom, Polygon):
                footprints.append(geom)
            elif hasattr(geom, 'geoms'):
                for poly in geom.geoms:
                    if isinstance(poly, Polygon) and poly.is_valid:
                        footprints.append(poly)
    
    return footprints


def create_bounding_box_mesh(bbox_dict):
    """Create a box mesh from bounding box dictionary"""
    x_min = bbox_dict['x_min']
    x_max = bbox_dict['x_max']
    y_min = bbox_dict['y_min']
    y_max = bbox_dict['y_max']
    z_min = bbox_dict['z_min']
    z_max = bbox_dict['z_max']

    # Create a box using trimesh
    box = trimesh.creation.box(
        extents=[x_max - x_min, y_max - y_min, z_max - z_min],
        transform=trimesh.transformations.translation_matrix([
            (x_min + x_max) / 2,
            (y_min + y_max) / 2,
            (z_min + z_max) / 2
        ])
    )

    return box


def buildings_to_3d_mesh(buildings_data):
    """Convert building footprints to 3D meshes"""
    print(" Converting to 3D meshes...")

    meshes = []
    # bbox_meshes = []  # DISABLED: Bounding box mesh generation
    positions = []
    heights = []
    areas = []
    bounding_boxes = []

    if isinstance(buildings_data, gpd.GeoDataFrame):
        # GeoDataFrame mode
        print(f" GeoDataFrame: {len(buildings_data)} rows")
        skipped_count = 0
        error_count = 0

        for idx, row in buildings_data.iterrows():
            if not isinstance(row.geometry, Polygon) or row.geometry.is_empty:
                skipped_count += 1
                print(f" Skipped row {idx}: geometry type = {type(row.geometry).__name__}, is_empty = {row.geometry.is_empty if hasattr(row.geometry, 'is_empty') else 'N/A'}")
                continue

            try:
                # Extrude polygon to 3D
                mesh = trimesh.creation.extrude_polygon(row.geometry, float(row['height']))

                # Remove bottom face (same as geometryGenerator.py)
                normals = mesh.face_normals
                keep_faces = np.where(normals[:, 2] > -0.9)[0]  # Remove faces with z-normal < -0.9 (bottom)
                mesh_open = mesh.submesh([keep_faces], append=True)

                mesh_open.apply_translation([0, 0, z_min])

                meshes.append(mesh_open)
                centroid = row.geometry.centroid
                positions.append([centroid.x, centroid.y])
                heights.append(float(row['height']))
                areas.append(row.geometry.area)

                # Extract bounding box (minx, miny, maxx, maxy from 2D footprint + z)
                minx, miny, maxx, maxy = row.geometry.bounds
                bbox_dict = {
                    "x_min": float(minx),
                    "x_max": float(maxx),
                    "y_min": float(miny),
                    "y_max": float(maxy),
                    "z_min": float(z_min),
                    "z_max": float(z_min + row['height'])
                }
                bounding_boxes.append(bbox_dict)

                # DISABLED: Create bounding box mesh
                # bbox_mesh = create_bounding_box_mesh(bbox_dict)
                # bbox_meshes.append(bbox_mesh)

            except Exception as e:
                error_count += 1
                print(f" Error row {idx}: {e}")
                continue

        print(f" Skipped: {skipped_count}, Errors: {error_count}, Success: {len(meshes)}")
    else:
        # Simple mode
        for bldg in buildings_data:
            if not isinstance(bldg['geometry'], Polygon) or bldg['geometry'].is_empty:
                continue

            try:
                mesh = trimesh.creation.extrude_polygon(bldg['geometry'], float(bldg['height']))

                # Remove bottom face (same as geometryGenerator.py)
                normals = mesh.face_normals
                keep_faces = np.where(normals[:, 2] > -0.9)[0]  # Remove faces with z-normal < -0.9 (bottom)
                mesh_open = mesh.submesh([keep_faces], append=True)

                mesh_open.apply_translation([0, 0, z_min])

                meshes.append(mesh_open)
                centroid = bldg['geometry'].centroid
                positions.append([centroid.x, centroid.y])
                heights.append(float(bldg['height']))
                areas.append(bldg['geometry'].area)

                # Extract bounding box
                minx, miny, maxx, maxy = bldg['geometry'].bounds
                bbox_dict = {
                    "x_min": float(minx),
                    "x_max": float(maxx),
                    "y_min": float(miny),
                    "y_max": float(maxy),
                    "z_min": float(z_min),
                    "z_max": float(z_min + bldg['height'])
                }
                bounding_boxes.append(bbox_dict)

                # DISABLED: Create bounding box mesh
                # bbox_mesh = create_bounding_box_mesh(bbox_dict)
                # bbox_meshes.append(bbox_mesh)

            except Exception as e:
                continue

    if not meshes:
        raise ValueError("No valid buildings to create mesh")

    print(f" Created {len(meshes)} building meshes")
    # print(f" Created {len(bbox_meshes)} bounding box meshes")  # DISABLED

    return (trimesh.util.concatenate(meshes),
            None,  # DISABLED: bbox_mesh always None
            positions, heights, areas, bounding_boxes)


def create_bottom_plate_with_holes(building_footprints):
    """Create bottom plate with holes for buildings with robust error handling"""
    print(" Creating bottom plate with building holes...")

    # Outer polygon (Section VII boundary)
    outer = Polygon([
        [x_min_VII, y_min_VII],
        [x_max_VII, y_min_VII],
        [x_max_VII, y_max_VII],
        [x_min_VII, y_max_VII]
    ])

    # Step 1: Filter and validate footprints
    valid_holes = []
    min_area = 1.0  # Minimum building area (m²) to prevent tiny polygons

    for fp in building_footprints:
        if fp.is_empty or not fp.is_valid:
            continue

        # Clip to outer boundary (prevent holes outside the plate)
        try:
            clipped = fp.intersection(outer)
            if clipped.is_empty or not clipped.is_valid:
                continue

            # Handle MultiPolygon results from intersection
            if hasattr(clipped, 'geoms'):
                for geom in clipped.geoms:
                    if isinstance(geom, Polygon) and geom.area >= min_area:
                        valid_holes.append(geom)
            elif isinstance(clipped, Polygon) and clipped.area >= min_area:
                valid_holes.append(clipped)
        except Exception:
            continue

    print(f" Valid building holes: {len(valid_holes)} (filtered from {len(building_footprints)})")

    if len(valid_holes) == 0:
        print(" No valid building footprints, creating flat plate")
        return make_patch(
            [x_min_VII, y_min_VII, z_min],
            [x_max_VII, y_min_VII, z_min],
            [x_max_VII, y_max_VII, z_min],
            [x_min_VII, y_max_VII, z_min]
        )

    # Step 2: Merge overlapping holes to prevent triangulation errors
    from shapely.ops import unary_union
    try:
        # Union all holes to resolve overlaps
        merged_holes = unary_union(valid_holes)

        # Convert back to list of polygons
        if hasattr(merged_holes, 'geoms'):
            valid_holes = [p for p in merged_holes.geoms if isinstance(p, Polygon)]
        elif isinstance(merged_holes, Polygon):
            valid_holes = [merged_holes]
        else:
            valid_holes = []

        print(f" After merging overlaps: {len(valid_holes)} holes")
    except Exception as e:
        print(f" Warning: Overlap merging failed: {e}")
        # Continue with unmerged holes

    if len(valid_holes) == 0:
        print(" No holes after processing, creating flat plate")
        return make_patch(
            [x_min_VII, y_min_VII, z_min],
            [x_max_VII, y_min_VII, z_min],
            [x_max_VII, y_max_VII, z_min],
            [x_min_VII, y_max_VII, z_min]
        )

    # Step 3: Simplify polygons to reduce complexity
    simplified_holes = []
    for hole in valid_holes:
        try:
            # Simplify with small tolerance (0.1m)
            simplified = hole.simplify(0.1, preserve_topology=True)
            if simplified.is_valid and not simplified.is_empty:
                simplified_holes.append(simplified)
            else:
                simplified_holes.append(hole)  # Use original if simplification fails
        except Exception:
            simplified_holes.append(hole)

    valid_holes = simplified_holes

    # Step 4: Create polygon with holes
    try:
        polygon_with_holes = Polygon(
            outer.exterior.coords,
            holes=[fp.exterior.coords for fp in valid_holes]
        )

        # Validate the result
        if not polygon_with_holes.is_valid:
            print(f" Warning: Created invalid polygon with holes")
            # Try to fix with buffer(0)
            polygon_with_holes = polygon_with_holes.buffer(0)
            if not polygon_with_holes.is_valid:
                raise ValueError("Cannot create valid polygon with holes")

    except Exception as e:
        print(f" Warning: Failed to create polygon with holes: {e}")
        print(f" Falling back to flat bottom plate")
        return make_patch(
            [x_min_VII, y_min_VII, z_min],
            [x_max_VII, y_min_VII, z_min],
            [x_max_VII, y_max_VII, z_min],
            [x_min_VII, y_max_VII, z_min]
        )
    
    # Step 5: Triangulate polygon with error recovery
    try:
        tri_data = trimesh.creation.triangulate_polygon(polygon_with_holes)

        # Create 3D mesh at z_min
        if isinstance(tri_data, tuple):
            vertices_2d, faces = tri_data
            vertices_3d = np.column_stack((vertices_2d, np.full(len(vertices_2d), z_min)))
            surface_mesh = trimesh.Trimesh(vertices=vertices_3d, faces=faces, process=False)
        else:
            surface_mesh = tri_data
            surface_mesh.apply_translation([0, 0, z_min])

        # Validate mesh quality
        if len(surface_mesh.faces) == 0:
            raise ValueError("Triangulation produced zero faces")

        print(f" Bottom plate: {len(valid_holes)} holes, {len(surface_mesh.faces)} faces")

        # Check for degenerate triangles
        degenerate_count = np.sum(surface_mesh.area_faces < 1e-10)
        if degenerate_count > 0:
            print(f" Warning: {degenerate_count} degenerate triangles detected")

        return surface_mesh

    except Exception as e:
        print(f" Warning: Triangulation failed: {e}")
        print(f" Attempting fallback: simplified hole removal...")

        # Fallback 1: Try with fewer holes (keep only largest buildings)
        try:
            if len(valid_holes) > 10:
                # Sort by area, keep largest 50%
                sorted_holes = sorted(valid_holes, key=lambda h: h.area, reverse=True)
                keep_count = max(5, len(sorted_holes) // 2)
                valid_holes = sorted_holes[:keep_count]

                print(f" Retrying with {len(valid_holes)} largest holes...")

                polygon_with_holes = Polygon(
                    outer.exterior.coords,
                    holes=[fp.exterior.coords for fp in valid_holes]
                )

                tri_data = trimesh.creation.triangulate_polygon(polygon_with_holes)

                if isinstance(tri_data, tuple):
                    vertices_2d, faces = tri_data
                    vertices_3d = np.column_stack((vertices_2d, np.full(len(vertices_2d), z_min)))
                    surface_mesh = trimesh.Trimesh(vertices=vertices_3d, faces=faces, process=False)
                else:
                    surface_mesh = tri_data
                    surface_mesh.apply_translation([0, 0, z_min])

                print(f" Bottom plate (reduced holes): {len(valid_holes)} holes, {len(surface_mesh.faces)} faces")
                return surface_mesh

        except Exception as e2:
            print(f" Fallback triangulation also failed: {e2}")

        # Fallback 2: Flat plate without holes
        print(f" Creating flat bottom plate (no holes)")
        return make_patch(
            [x_min_VII, y_min_VII, z_min],
            [x_max_VII, y_min_VII, z_min],
            [x_max_VII, y_max_VII, z_min],
            [x_min_VII, y_max_VII, z_min]
        )


def generate_geometry_toml(x, output_file="geometry.toml"):
    """Generate geometry.toml for m-AIA (same as geometryGenerator.py)"""
    filenames = {
        0: "./stl/inlet.stl",
        1: "./stl/outlet.stl",
        2: "./stl/left.stl",
        3: "./stl/right.stl",
        4: "./stl/top.stl",
        5: "./stl/bottom_around_plate.stl",
        6: f"./stl/bottom_plate_{x}.stl",
        7: f"./stl/buildings_{x}.stl",
        # 8: f"./stl/bounding_boxes_{x}.stl"  # DISABLED
    }

    bc = {
        0: 1000,
        1: 4000,
        2: 3020,
        3: 3020,
        4: 3020,
        5: 3020,
        6: 2000,
        7: 2000,
        # 8: 2000  # DISABLED
    }

    body_segments = {
        "body_segments.inlet": 0,
        "body_segments.outlet": 1,
        "body_segments.left": 2,
        "body_segments.right": 3,
        "body_segments.top": 4,
        "body_segments.bottom_around_plate": 5,
        "body_segments.bottom_plate": 6,
        "body_segments.buildings": 7,
        # "body_segments.bounding_boxes": 8  # DISABLED
    }

    geometry = {
        "noSegments": 8,  # Changed from 9 to 8
        "inOutSegmentsIds": [0, 1],
    }

    for idx, fname in filenames.items():
        geometry[f"filename.{idx}"] = fname

    geometry.update(body_segments)

    for idx, val in bc.items():
        geometry[f"BC.{idx}"] = val

    with open(os.path.join(geometry_path, output_file), "w") as f:
        toml.dump(geometry, f)

    print(f" geometry.toml generated")


# ========================================
# MAIN EXECUTION
# ========================================

def main():
    print("=" * 60)
    print("Real City Geometry Generator for urbanFlowGen")
    print("=" * 60)
    
    # 1. Create CFD domain walls
    create_cfd_walls()
    
    # 2. Sample or use exact location
    print("\n Determining location...")
    sampled_lat, sampled_lon, city_name, utm_zone = sample_location_in_city(
        force_lat=args.lat,
        force_lon=args.lon,
        force_utm_zone=args.utm_zone
    )
    print(f"   City/Source: {city_name}")
    print(f"   Location: ({sampled_lat:.6f}, {sampled_lon:.6f})")
    print(f"   UTM Zone: {utm_zone}")

    # 3. Fetch building data
    print("\n Fetching building data...")
    radius = city_config['settings']['collection_radius_meters']
    data_source = city_config['settings']['data_source']
    
    bbox = calculate_bbox_for_circle(sampled_lat, sampled_lon, radius)
    print(f"   BBOX: {bbox}")

    if data_source == "overture_geopandas":
        buildings = fetch_buildings_geopandas(bbox, utm_zone)
    elif data_source == "global_building_atlas":
        buildings = fetch_buildings_wfs(bbox, utm_zone)

        # Fallback to Overture Maps if Global Building Atlas fails
        if buildings is None:
            print("\n Global Building Atlas unavailable (server may be under maintenance)")
            print(" Falling back to Overture Maps...")
            buildings = fetch_buildings_geopandas(bbox, utm_zone)
            if buildings is not None:
                print(" Successfully fetched from Overture Maps (fallback)")
    else:
        buildings = fetch_buildings_simple(bbox, utm_zone)
    
    if buildings is None or len(buildings) == 0:
        print("\n No buildings found. Try different location or increase radius.")
        sys.exit(1)
    
    # 4. Filter circular domain
    result = filter_circular_buildings(buildings, sampled_lat, sampled_lon, radius, utm_zone)
    if result is None:
        print("\n No buildings within circular domain.")
        sys.exit(1)
    
    buildings_circular, center_utm = result
    
    # 5. Transform to section VII with safety margins
    print("\n Processing buildings...")
    buildings_transformed, safe_zone_center = transform_to_section_vii(buildings_circular, center_utm)
    
    # 6. Apply rotation around safe zone center
    buildings_rotated, angle_deg = apply_rotation(buildings_transformed, safe_zone_center)
    
    # 7. Extract 2D footprints for bottom plate holes
    print("\n Creating bottom plate...")
    building_footprints = extract_building_footprints(buildings_rotated)
    
    # 8. Create bottom plate with holes (same as geometryGenerator.py)
    bottom_plate = create_bottom_plate_with_holes(building_footprints)
    
    # 9. Convert to 3D building meshes
    print("\n  Converting buildings to 3D...")
    buildings_mesh, bbox_mesh, positions, heights, areas, bounding_boxes = buildings_to_3d_mesh(buildings_rotated)

    # 10. Export STL files
    print("\n Exporting STL files...")
    bottom_plate_file = os.path.join(stl_path, f'bottom_plate_{sample_id}.stl')
    buildings_file = os.path.join(stl_path, f'buildings_{sample_id}.stl')
    # bboxes_file = os.path.join(stl_path, f'bounding_boxes_{sample_id}.stl')  # DISABLED

    bottom_plate.export(bottom_plate_file, file_type='stl_ascii')
    buildings_mesh.export(buildings_file, file_type='stl_ascii')

    # DISABLED: Bounding box mesh export
    # if bbox_mesh is not None:
    #     bbox_mesh.export(bboxes_file, file_type='stl_ascii')
    #     print(f"{bboxes_file}")

    print(f" {bottom_plate_file}")
    print(f" {buildings_file}")
    
    # 11. Save metadata
    print("\n Saving metadata...")

    # Extract building_sizes from rotated bounding boxes (for gridGenerator compatibility)
    building_sizes = []
    for bbox in bounding_boxes:
        x_width = bbox["x_max"] - bbox["x_min"]
        y_width = bbox["y_max"] - bbox["y_min"]
        building_sizes.append([x_width, y_width])

    metadata = {
        "sample_id": sample_id,
        "city_name": city_name,
        "sampled_location": {
            "lat": round(sampled_lat, 6),
            "lon": round(sampled_lon, 6)
        },
        "collection_radius_m": radius,
        "rotation_angle_deg": 0,  # gridGenerator should not rotate again (already rotated)
        "compass_rotation_deg": round(angle_deg, 2),  # Actual rotation applied (for reference)
        "data_source": data_source,
        "building_count": len(positions),
        "building_positions": positions,  # Rotated positions
        "building_sizes": building_sizes,  # Rotated AABB sizes (for gridGenerator)
        "building_heights": heights,
        "building_areas": areas,
        "building_bounding_boxes": bounding_boxes,
        "domain": {
            "x_min": x_min, "x_max": x_max,
            "y_min": y_min, "y_max": y_max,
            "z_min": z_min, "z_max": z_max
        },
        "section_VII": {
            "x_min": x_min_VII, "x_max": x_max_VII,
            "y_min": y_min_VII, "y_max": y_max_VII
        }
    }
    
    metadata_file = os.path.join(stl_path, f'{sample_id}_metadata.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4)
    
    print(f" {metadata_file}")
    
    # 12. Generate geometry.toml
    print("\n Generating m-AIA configuration...")
    generate_geometry_toml(sample_id)
    
    # 13. Summary
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE!")
    print("=" * 60)
    print(f" City: {city_name}")
    print(f" Location: ({sampled_lat:.6f}, {sampled_lon:.6f})")
    print(f" Buildings: {len(positions)}")
    print(f" Rotation: {angle_deg:.2f}°")
    print(f" Output: ./{sample_id}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
