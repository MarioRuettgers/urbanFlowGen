import toml

# Load config.toml
config = toml.load('config.toml')
refine = config['grid_mAIA']
sim = config['sim_mAIA']
ref = config['reference']
glob = config['global']

# Extract values
timeSteps = sim['tau']
Re = sim['Re']
initStartTime=sim['tau_re_start']
initTime=sim['Delta_tau_re']
solutionInterval=sim['Delta_tau_s']
restartInterval=sim['Delta_tau_r']
restartFile=sim['RESTART']
restartTimeStep=sim['tau_r']
postProcessing=sim['TIME-AVERAGING']
pp_averageStartTimestep=sim['tau_a_start']
pp_averageStopTimestep=sim['tau_a_stop']
pp_averageInterval=sim['Delta_tau_a']
pp_averageRestart=sim['RESET']
calcBcResidual=sim['MONITOR']

maxRfnmntLvl=refine['RL_max']

l=ref['l']
RF=refine['RF']
L=glob['x_max']-glob['x_min']

# cell size at max refinement level
del_x = (RF * L)/(2**maxRfnmntLvl)

# reference length as a multiple of del_x
l_norm = l/del_x

# Create properties dictionary
properties = {
    # -------------- APPLICATION SETTINGS  --------------
    'virtualSurgery': False,
    'fileProcessingMode': 0,
    'gridGenerator': False,
    'flowSolver': True,
    'restartFile': restartFile,
    'initRestart': False,
    'scratchSize': 80.0,
    'nrHaloLayer': 1,
    'calcBcResidual': calcBcResidual,
    'multiSolverGrid': True,
    'multiSolver': True,

    # -------------- MASSIVE PARALLEL  --------------
    'lbm': True,
    'partitionCellOffspringThreshold': 50000,

    # -------------- APPLICATION ENVIRONMENT  --------------
    'outputDir': './out/',
    'geometryInputFileName': 'geometry.toml',
    'geometryPropertyFile': 'geometry.toml',
    'gridInputFileName': 'grid.Netcdf',
    'gridOutputFileName': 'grid.Netcdf',

    # -------------- SOLUTION PROPERTIES ----------------
    'solutionInterval': solutionInterval,
    'restartInterval': restartInterval,
    'residualInterval': 50000,
    'restartTimeStep': restartTimeStep,

    # -------------- NUMERICAL PROPERTIES --------------
    'solvertype.default': "MAIA_UNIFIED",
    'executionRecipe': "RECIPE_BASE",
    'solvertype.0': "MAIA_LATTICE_BOLTZMANN",
    'solvertype.1': "MAIA_POST_DATA",
    'postprocessingOrder_0': [0, 1],
    'noVariables.1': 14,

    'postProcessing': postProcessing,
    'noPostProcessing': 1,
    'postProcessingSolverIds': [0],
    'postProcessingType_0': "POSTPROCESSING_LB",
    'postProcessingOps_0': ["PP_AVERAGE_IN"],

    'pp_averageStartTimestep': pp_averageStartTimestep,
    'pp_averageStopTimestep': pp_averageStopTimestep,
    'pp_averageInterval': pp_averageInterval,
    'pp_averageRestartInterval': 50000,
    'pp_averageRestart': pp_averageRestart,

    'solverMethod.0': "MAIA_LATTICE_CUMULANT",

    # -------------- MISC DIMENSIONAL PROPERTIES --------------
    'nDim': 3,
    'noDistributions': 27,
    'timeSteps': timeSteps,
    'noSolvers': 2,
    'multiBCTreatment': "W-I-P",

    # ------------ FLOW INITIALIZATION -----------
    'initMethod': "LB_FROM_ZERO_INIT",
    'tanhInit': True,
    'initRe': 100.0,
    'initTime': initTime,
    'initStartTime': initStartTime,

    # -------------- FLOW VARIABLES --------------
    'Ma': 0.03,
    'Re': Re,
    'referenceLengthLB': l_norm,
    'lbControlInflow': 0,
    'externalForcing': False,

    # ----------- GEOMETRY SEGMENTATION ----------
    'inflowSegmentIds': [0],
    'maxNoCells': 40000000,
    'reducedComm': True,
    'initVelocityMethod': "fromSTL",
    'bndNormalMethod': "fromSTL",
    'interpolationDistMethod': "STD",
    'maxRfnmntLvl': maxRfnmntLvl
}

# Write dictionary to properties_run.toml
with open("properties_run.toml", "w") as f:
    toml.dump(properties, f)

print("✅ properties_run.toml written in structured TOML format.")

