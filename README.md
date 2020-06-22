# 2019-2020 Cmpe 493: Term Project

In this project, we have tried to implement a predictor for
[bb-norm](https://sites.google.com/view/bb-2019/home). This implementation
contains only *Habitats* and *Phenotypes* predictions.

## Preparation
Before running the model, you have to create *caches* and *w2v* data. If 
you have received the source code from us, you should already have
a pre-cached w2v data. However, 
other caches must be created by you, and required data should be in place. 

#### Required Packages
 - tensorflow
 - torch
 - transformers
 - tqdm
 - nltk
 - ijson
 
You should have already setup these packages, especially nltk, since it requires extra
downloads.

#### File Placement
We have predefined the file locations in the code. You should obey these placements
in order to make the program run correctly.
 - Extract the contents of BioNLP-OST-2019_BB-norm for dev, train and test into ```../data```
directory.
 - Put the OntoBiotope_BioNLP-OST-2019.obo file into ```../data``` directory
 - Create a directory called ```predictions``` at location ```../```, which can 
 be accessed like ```../predictions``` 

The file placement should be like this: 
    
    data/
        BioNLP-OST-2019_BB-norm_dev/
            **
        BioNLP-OST-2019_BB-norm_test/
            **
        BioNLP-OST-2019_BB-norm_train/
            **
        OntoBiotope_BioNLP-OST-2019.obo
    src/
        **source code
        w2v.pkl
    predictions/
    
Scripts should be called inside the *src* directory.

## Execution
#### 1. w2v_parser.py
If you do not have a pre-cached *w2v* data. You should create it by yourself.
 - Obtain *word-vectors.json* file from the organizers. We have used 
 vectors of 100 dimension.
 - Execute the command ```./w2v_parser.py <word-vectors.json-file-path> ./w2v.pkl```
 - ```w2v.pkl``` file should be created.
 
Parsing can take long time. Let it continue running unless it crashed.
 
 
#### 2. cache.py
This caching is prepared for *test* data set. If you want to also create caches for *dev* and *traing*,
you should specify them at the *cache.py* file. 
 - Execute the command ```./cache.py <cache-directory>```, where the 
 ```<cache-directory>``` should be a directory for placing cache contents
 
 Caching can take long time. Let it continue running unless it crashed.

#### 3. main.py
This is where our model runs. If you have successfully completed the previous steps, *w2v2_parser* and *cache*, this script should
run quickly. You can try different models and see their results in a very short time thanks to caching.
We have provided a bash script called ```run.sh``` which lets you run multiple processes for speeding up.
Expect a 4GB increase in memory usage. You should define number of processes in the ```run.sh``` script 
according to your machine's physical and logical cores, besides you should specify the cache location. 
We do not recommend using GPU for tensorflow, because
we have observed that it slow downs the execution. This is due to lots of short calculations and
as a result, communication overhead.

If you want to call directly ```main.py``` script, you can call it like

    ./main.py <cache-directory> <start-index> <length>
Where the ```<cache-directory>``` is the directory that contains caches, ```<start-index>``` is the nth file 
this script will start to run, finally ```<length>``` is the description of how many files this script will run.
For example, if you have 90 test file, calling ```./main.py ../caches 10 5``` will run the files between 
10 inclusive and 15 exclusive which are determined by alphabetically ascending sort.
## Support
If you have found a bug or have a question, please create an issue and report or ask it at our repo [bb-norm](https://github.com/bwqr/bb-norm).
 
