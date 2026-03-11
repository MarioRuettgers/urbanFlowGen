##################################
import sys

sys.path.append('/Users/marioruttgers/venvs/pipeline/lib/python3.7/site-packages')

##################################
#Load modules
import nrrd
import numpy as np
from paraview.simple import *
from paraview import servermanager as sm
import vtk
from scipy import ndimage
from skimage.measure import label
from vtk.util import numpy_support
from stl import mesh
import pyvista as pv
import pymeshfix as mf
##################################

#Load mesh:
box_mesh = mesh.Mesh.from_file('box.stl')

#Extract vectors and normals of each triangle
normals=box_mesh.normals
v_0=box_mesh.v0
v_1=box_mesh.v1
v_2=box_mesh.v2

#Stack the to one array
#0-2 v_0, 3-5 v_1, 6-8 v_2, 9-11 normals
data_array=np.hstack((v_0,v_1,v_2,normals))

#Create one list for each boundary
inlet_tri=[]
outlet_tri=[]
wall_right_tri=[]
wall_left_tri=[]
wall_top_tri=[]
wall_bottom_tri=[]

#Distribute the current triangles to their corresponding list
for i in range(data_array.shape[0]):

   if np.absolute(data_array[i,9])==1 and data_array[i,0] < 0:

      inlet_tri.append(data_array[i])

   elif np.absolute(data_array[i,9])==1 and data_array[i,0] > 0:

      outlet_tri.append(data_array[i])

   elif np.absolute(data_array[i,10])==1 and data_array[i,1] < 0:

      wall_right_tri.append(data_array[i])
   
   elif np.absolute(data_array[i,10])==1 and data_array[i,1] > 0:

      wall_left_tri.append(data_array[i])
   
   elif np.absolute(data_array[i,11])==1 and data_array[i,2] < 0:

      wall_bottom_tri.append(data_array[i])
   
   else:

      wall_top_tri.append(data_array[i])

# Convert lists to np.arrays
inlet_tri_array = np.asarray(inlet_tri)
outlet_tri_array = np.asarray(outlet_tri)
wall_right_tri_array = np.asarray(wall_right_tri)
wall_left_tri_array = np.asarray(wall_left_tri)
wall_top_tri_array = np.asarray(wall_top_tri)
wall_bottom_tri_array = np.asarray(wall_bottom_tri)

def write_stl(file, array):
          with open(file, "w") as file:
              file.write("solid ascii\n")
              for i in range(array.shape[0]):
                  file.write(
                      "   facet normal "
                      + str(array[i, 9])
                      + " "
                      + str(array[i, 10])
                      + " "
                      + str(array[i, 11])
                      + "\n"
                  )
                  file.write("    outer loop\n")
                  file.write(
                      "     vertex "
                      + str(array[i, 0])
                      + " "
                      + str(array[i, 1])
                      + " "
                      + str(array[i, 2])
                      + "\n"
                  )
                  file.write(
                      "     vertex "
                      + str(array[i, 3])
                      + " "
                      + str(array[i, 4])
                      + " "
                      + str(array[i, 5])
                      + "\n"
)
                  file.write(
                      "     vertex "
                      + str(array[i, 6])
                      + " "
                      + str(array[i, 7])
                      + " "
                      + str(array[i, 8])
                      + "\n"
                  )
                  file.write("    endloop\n")
                  file.write("   endfacet\n")
              file.write(" endsolid")

# Write STLs
# INLET
write_stl("inlet.stl", inlet_tri_array)
# OUTLET
write_stl("outlet.stl", outlet_tri_array)
# WALLS
write_stl("wall_right.stl", wall_right_tri_array)
write_stl("wall_left.stl", wall_left_tri_array)
write_stl("wall_top.stl", wall_top_tri_array)
write_stl("wall_bottom.stl", wall_bottom_tri_array)

