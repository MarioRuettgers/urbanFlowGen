#!/bin/bash

# === CONFIGURATION ===

# Activate virtual environment
source ./venv/bin/activate

# Scripts
GEOMETRY_SCRIPT="./geometryGenerator_realCity.py"
#GEOMETRY_SCRIPT="./geometryGenerator.py"
GEOMETRY_SCRIPT="./geometryGenerator.py"
GRID_SCRIPT="./gridGenerator.py"
SIM_SCRIPT="./simGenerator.py"

# SLURM scripts
SLURM_SCRIPT_GRID="grid.sh"
SLURM_SCRIPT_RUN="run_gpu.sh"

# === FUNCTIONS ===

is_integer() {
    [[ "$1" =~ ^-?[0-9]+$ ]]
}

ask_for_range() {
    read -p "Enter the minimum integer value: " min
    while ! is_integer "$min"; do
        echo "Invalid input. Please enter an integer."
        read -p "Enter the minimum integer value: " min
    done

    read -p "Enter the maximum integer value: " max
    while ! is_integer "$max" || [ "$max" -lt "$min" ]; do
        if ! is_integer "$max"; then
            echo "Invalid input. Please enter an integer."
        else
            echo "Maximum must be greater than or equal to minimum ($min)."
        fi
        read -p "Enter the maximum integer value: " max
    done
}

create_folder_if_missing() {
    local folder="$1"
    if [ ! -d "$folder" ]; then
        mkdir -p "$folder"
        echo "📁 Created folder: $folder"
    fi
}

generate_case() {
    local i="$1"
    local TARGET_FOLDER="./$i"
    local STL_FOLDER="$TARGET_FOLDER/stl"
    local OUT_FOLDER="$TARGET_FOLDER/out"

    echo -e "\nStarting case: $i"

    create_folder_if_missing "$STL_FOLDER"
    create_folder_if_missing "$OUT_FOLDER"

    # Geometry generation
    python "$GEOMETRY_SCRIPT" "$i" || { echo "Geometry generation failed for $i"; return 1; }

    # Grid properties
    python "$GRID_SCRIPT" "$i" || { echo "Grid generation failed for $i"; return 1; }
    mv properties_grid.toml "$TARGET_FOLDER"

    # Simulation properties
    python "$SIM_SCRIPT" || { echo "Simulation generation failed for $i"; return 1; }
    mv properties_run.toml "$TARGET_FOLDER"

    # Copy SLURM scripts
    cp "$SLURM_SCRIPT_GRID" "$SLURM_SCRIPT_RUN" "$TARGET_FOLDER"

    # Submit jobs
    cd "$TARGET_FOLDER"
    if [ -f "$SLURM_SCRIPT_RUN" ]; then
        sed -i "s/^#SBATCH --job-name=.*/#SBATCH --job-name=$i/" "$SLURM_SCRIPT_RUN"
        jobid=$(sbatch "$SLURM_SCRIPT_GRID" | awk '{print $4}')
        sbatch --dependency=afterok:$jobid "$SLURM_SCRIPT_RUN"
        echo "Submitted SLURM jobs for case $i (grid → run)"
    else
        echo "Missing $SLURM_SCRIPT_RUN in $TARGET_FOLDER"
    fi
    cd - >/dev/null
}

# === MAIN ===

ask_for_range

for i in $(seq "$min" "$max"); do
    generate_case "$i"
done

