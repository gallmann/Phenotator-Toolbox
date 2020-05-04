# Phenotator Toolbox

This repository contains a whole Toolbox that can be used for Object Detection Problems in aerial settings. The repository has the following four subfolders:

#### AnnotationTool
This folder is the Android Studio project folder of the Phenotator FieldAnnotator app. The source code is found within [this](AnnotationTool/app/src/main/java/com/masterthesis/johannes/annotationtool) subfolder.

#### Desktop-Preprocessing
This folder contains the code for the preprocessing tool with user interface. 

#### Documentation
This folder contains usage instructions, the article pdf as well as some draw.io files of diagrams used within the publication.

#### Tensorflow
This folder contains all code of the command line tool. It is self contained meaning all dependencies such as code from the Tensorflow object detection api is included in this folder. The subfolder [Tensorflow/utils](Tensorflow/utils) contains helper scripts which may be used by multiple main scripts in the [Tensorflow](Tensorflow) folder.


## Installation and Usage
For installation and usage instructions refer to the following document: [Documentation.pdf](Documentation/Documentation.pdf). Alternatively, the [tutorial videos](Documentation/Tutorial%20Videos) are a good starting point.
