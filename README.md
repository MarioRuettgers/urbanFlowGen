# urbanFlowGen
urbanFlowGen is an open-source Python library for generating synthetic urban Computational Fluid Dynamics (CFD) scenarios tailored for machine learning applications. It provides a fully automated pipeline for:

- Step 1: Sampling physically realistic atmospheric inflow conditions from reanalysis data,
- Step 2: Generating randomized 3D urban geometries with customizable features,
- Step 3: Creating property files for generating computational meshes using open-source grid generation tools,
- Step 4: Creating property files for setting up CFD simulations for both CPU- and GPU-based solvers (e.g., OpenFOAM, m-AIA).

The library is modular and extensible, making it easy to integrate with custom solvers or simulation workflows. It is designed to support researchers and practitioners working on data-driven urban flow modeling, offering a scalable solution for producing diverse and physically realistic training datasets.

When executing the bash script "virtualEnv.sh", a Python virtual environment is created, the modules listed in "requirements.txt" are installed with pip, and the virtual environment is activated. The directory of the virtual environment can be adjusted in "VENV_DIR=..."

With the file "getReanalysisData.py", reanalysis data from the era5 dataset are downloaded. They are required for Step 1 of the pipeline. The user can specify the year and area (min. and max. latitudinal and longitudinal coordinates) of which hourly data of the "10m_u_component_of_neutral_wind", "10m_v_component_of_neutral_wind" data are stored. Furthermore, the target directory needs to be specified by the user.  
