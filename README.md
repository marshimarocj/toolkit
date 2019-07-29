# python toolkit
common functions and data structures used in experiments

## ds.py
common data structures not provided in python standard library
* DisjointSet: disjoint set
* DoubleLinkedList: double linked list
* Heap: actually python standard library provides heap operations. I wrote it before I knew the above fact>.<

## sample.py
common sampling strategies
* ReservoirSampling: reservoir sampling from stream
* samplePairs: uniformly sample pairs from n^2 pairs without really constructing these pairs

## vision.py
vision related utility functions, depending on opencv and ffmpeg
* isValidImg: check whether the downloaded image is a valid complete image. 
* shotDetect: shot detection using ffmpeg
* keyFrame: key frame extraction using ffmpeg

## osm.py
parser for open street map format
* RoadExtractor: extract road information
* BuildingExtractor: extract building information
* downloadOSM: download open street map given the rectangle of GPS coordinate

## toolkit.py
utilities
* printTimeLen: print formatted time duration, usually for profiling
* set_logger: logging helper
* dirInteractiveChecker: interactive directory checking
