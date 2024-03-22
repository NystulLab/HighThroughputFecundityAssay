# High Throughput Drosophila Fecundity Assay

## Raw data and figures
### Contents
`Data` : The raw data from the egg counts <br>
`Code` : R Notebooks used to generate figures from the raw data. <br>
`Results` : Output from R Notebooks <br>

## RoboCam
### Contents
'RoboCam" : Python scripts used to operate the RoboCam

## Image segmentation to identify eggs
### Contents
`fly_egg_counting` : A folder containing some test images and the flyModel2 model files <br>
`egg_counting_with_flyModel2.ipynb` : Google colab notebook that contains the image analysis pipeline <br>
`flymodel2.zip` : Stardist trained model used in the pipeline

### User inputs

**mainPath** : path to where the `fly_egg_counting` folder has been saved <br>
**ExperimentName** : Name of the folder that contains the input jpg images <br>
**EstimatedWellDiameter** : Well diameter in pixels <br><br>

<img width="1398" alt="Screenshot 2024-03-11 at 4 42 35 PM" src="https://github.com/okeashwini/fly_egg_counting/assets/26334605/1055911b-5033-45b1-bbe4-86c1e1226021">

<br><br>
### References <br> 

Uwe Schmidt, Martin Weigert, Coleman Broaddus, and Gene Myers.
[Cell Detection with Star-convex Polygons.](https://arxiv.org/abs/1806.03535)
International Conference on Medical Image Computing and Computer-Assisted Intervention (MICCAI), Granada, Spain, September 2018.

Martin Weigert, Uwe Schmidt, Robert Haase, Ko Sugawara, and Gene Myers.
[Star-convex Polyhedra for 3D Object Detection and Segmentation in Microscopy.](http://openaccess.thecvf.com/content_WACV_2020/papers/Weigert_Star-convex_Polyhedra_for_3D_Object_Detection_and_Segmentation_in_Microscopy_WACV_2020_paper.pdf)
The IEEE Winter Conference on Applications of Computer Vision (WACV), Snowmass Village, Colorado, March 2020

