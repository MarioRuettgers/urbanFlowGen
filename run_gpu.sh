#!/bin/bash -x

#SBATCH --job-name=1
#SBATCH --account=urbanflow
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --output=gpu-out
#SBATCH --error=gpu-err
#SBATCH --time=24:00:00
#SBATCH --partition=dc-gpu
#SBATCH --gres=gpu:4

module use $OTHERSTAGES
module load Stages/2024
module load NVHPC/24.3-CUDA-12 OpenMPI FFTW.MPI PnetCDF Boost.Python
module load MPI-settings/CUDA
module load UCX-settings/RC-CUDA

srun /p/scratch/urbanflow/ruettgers1/2025_3D_square_cylinder_Re_9300/Solver/build_nvhpc_production/bin/maia properties_run.toml
