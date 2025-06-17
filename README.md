# urbanFlowGen
urbanFlowGen is an open-source Python library for generating synthetic urban Computational Fluid Dynamics (CFD) scenarios tailored for machine learning applications. It provides a fully automated pipeline for:

- Step 1: Generating randomized 3D urban geometries with customizable features,
- Step 2: Creating property files for generating computational meshes using open-source grid generation tools,
- Step 3: Creating property files for setting up CFD simulations for both CPU- and GPU-based solvers (e.g., OpenFOAM, m-AIA).

The library is modular and extensible, making it easy to integrate with custom solvers or simulation workflows. It is designed to support researchers and practitioners working on data-driven urban flow modeling, offering a scalable solution for producing diverse and physically realistic training datasets.

When executing the bash script "virtualEnv.sh", a Python virtual environment is created, the modules listed in "requirements.txt" are installed with pip, and the virtual environment is activated. The directory of the virtual environment can be adjusted in "VENV_DIR=...".


