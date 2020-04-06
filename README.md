# Capstone Project code

Some python packages need to be installed beforehand:

```
$ sudo apt install python-opencv python-numpy python-picamera
```

Run the following from the terminal in the directory this repository is extracted:

```
$ ./run.py
```

Changing `DOWNSAMPLE_SIZE` in the code will affect accuracy and performance. A larger downsample size is more accurrate but slower. This number shouldn't be higher than the lowest dimension of the camera resolution.
