import toml
import os

# Load parameters from config.toml
config = toml.load('config.toml')
refine = config['grid_mAIA']

# Extract values
reductionFactor = refine['RF']
minLevel = refine['RL_min']
maxUniformRefinementLevel = refine['RL_max_unif']
maxRfnmntLvl = refine['RL_max']
maxBoundaryRfnLvl = refine['RL_max']
smoothDistance = refine['Theta']
localMinBoundaryThreshold = refine['Gamma']

# Create extended lists with final value = 3x
smoothDistanceList = [smoothDistance] * 8 + [smoothDistance * 3]
localMinThresholdList = [localMinBoundaryThreshold] * 8 + [localMinBoundaryThreshold * 3]

# Assemble dictionary
properties = {
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
    'localRfnMethod': 2,
    'localRfnBoundaryIds': list(range(9)),
    'smoothDistance': smoothDistanceList,
    'localMinBoundaryThreshold': localMinThresholdList,
    'maxNoCells': 300_000_000,
    'partitionCellOffspringThreshold': 50_000_000,

    'solver': {
        '0': {'geometryInputFileName': 'geometry.toml'},
        '1': {'geometryInputFileName': 'geometry.toml'}
    }
}

# Write to properties_grid.toml
with open('properties_grid.toml', 'w') as f:
    toml.dump(properties, f)

print("✅ properties_grid.toml has been generated.")
