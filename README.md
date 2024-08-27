# High Throughput Drosophila Fecundity Assay

## Raw data and figures
### Contents
`Data` : The raw data from the egg counts <br>
`Code` : R Notebooks used to generate figures from the raw data. <br>
`Results` : Output from R Notebooks <br>

## RoboCam
Also available at https://github.com/raymondWWW/FlyCam-Support-Materials
### Contents
`RoboCam` : Python scripts used to operate the RoboCam
`FlyCam-Support-Materials` : Manuals and STL files for 3D printing. 

## Fly Transfer Device
Also available at https://github.com/CCCofficial/FlyTransferCups_v10.git
### Description
FlyCup for transfering fruit flies in standard 48 well trays. A fruit fly transfer lid is constructed from a layer of nylon mesh bonded between an array of cups (FlyCup48_cup_v10.stl) and holes (FlyCup48_stud_v10.stl). Studs in the hole layer pass through corresponding holes in the cup and nylon layers, creating individual gas exchange tops for each well. A hot soldering iron, guided by holes in a metal template, creates holes in the nylon mesh. The metal template is thin sheet metal with 2 mm diameter holes drilled at the stud locations. The final assembly studs are bonded with cyanoacrylate glue. When placed on a CO2 plate, anesthetized flies fall into their corresponding cup, enabling the plate to be replaced and flipped, simultaneously transferring all flies into new wells. The cup and holes are fabricated by SLA 3D printing in LEDO 6060 Resin which provides high dimensional stability and good temperature resistance. Natural white is used to provide good contrast against the dark fruit flies. Designed by Todd G. Nystul (University of California, San Francisco, Department of Anatomy) and Thomas G. Zimmerman (IBM Research-Almaden and Center for Cellular Construction).
### Contents
STL files for 3D printing of the Fly Transfer Device pieces

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

