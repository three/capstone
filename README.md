# Capstone Project code

Some python packages need to be installed beforehand. Terminal commands won't work on Windows, so you need to make sure you're using python 3 and have the opencv and numpy packages installed. The packages must be for python 3, the equivilent python 2 packages will not work.

```
$ sudo apt install python3 python3-opencv python3-numpy
```

This repository can be downloaded by installing then running git, then entering the capstone directory. Alternatively you can download a zip archive under "Clone or download".

```
$ sudo apt install git
$ git clone https://github.com/three/capstone.git
$ cd capstone
```

To run from a video file you can pass in the name of the video file. For instance, running it on the included `test.mp4`

```
$ ./run.py test.mp4
```

If you pass in a number it attempts to use the webcam associated with the number, usually 0 if there's only one. Some webcam buffering is a bit weird.

```
$ ./run.py 0
```

Some issues may be solved by not having all packages fully updated.

```
$ sudo apt update
$ sudo apt dist-upgrade
```

Running it will create two windows to let you know what the program is seeing. To move on to the next frame you need to press enter while one of these windows is focused. This can be changed by removing the `cv2.waitKey()` line.

Changing `DOWNSAMPLE_SIZE` in the code will affect accuracy and performance. A larger downsample size is more accurrate but slower. This number shouldn't be higher than the lowest dimension of the camera resolution.

As of now the code to move the trimmer motor is not present (I can't test it since I don't have a motor).
