# Capstone Project code

## Windows

First you need to [download python 3][python]. The latest version as writing this is 3.8.2 but something a little out of date is probably fine. After you download it you can see the current version by opening up cmd.exe and passing the `--version` flag.

[python]: https://www.python.org/

```
> python --version
Python 3.8.2
```

If you installed python but the command isn't there or it's the wrong version you probably don't have have the right directory in your path. In this case you can reference the executable directly. The location might be different.

```
> "C:\Users\Eric\AppData\Local\Programs\Python\Python38-32\python.exe" --version
Python 3.8.2
```

In this case every time you reference python you instead need to reference the entire path.

On Windows OpenCV and numpy can be installed with pip, which should be included in the python installation.

```
> python -m pip install numpy opencv-python opencv
```

Instead of using git to get download the repository, you can instead click the green "Clone or download" and "Download Zip". Extract it somewhere you remember and `cd` into that directly from cmd. This should be the directory with the run.py file.

```
> cd "C:\Users\Eric\Desktop\capstone-master"
```

It can be run from that directory. What `<args>` should be is described in usage instructions.

```
> python run.py <args>
```

## Rasbien (for Rasberry Pi)

Rasbien inlcudes python 2 but the code needs to be run in python 3. You can download python3 along with numpy and opencv directly from the rasbien and debian repos.

```
$ sudo apt install python3 python3-opencv python3-numpy
```

The easiest way to download everything on Rasbien is with git. You need to install git and then you can clone the repository and `cd` into the directory.

```
$ sudo apt install git
$ git clone https://github.com/three/capstone.git
$ cd capstone
```

The script has the right [shebang][shebang] to automatically choose and run with the right python version.

[shebang]: https://en.wikipedia.org/wiki/Shebang_(Unix)

```
$ ./run.py <args>
```

See usage instructions for what `<args>` should be.

## Usage instructions

To run from a video file you can pass in the name of the video file. For instance, running it on the included `test.mp4`

```
$ ./run.py test.mp4
```

If you pass in a number it attempts to use the webcam associated with the number, usually 0 if there's only one. Some webcam buffering is a bit weird.

```
$ ./run.py 0
```

Running it will create two windows to let you know what the program is seeing. To move on to the next frame you need to press enter while one of these windows is focused. This can be changed by removing the `cv2.waitKey()` line, although it doesn't always visibly draw the frames if you do this.

Changing `DOWNSAMPLE_SIZE` in the code will affect accuracy and performance. A larger downsample size is more accurrate but slower. This number shouldn't be higher than the lowest dimension of the camera resolution.

As of now the code to move the trimmer motor is not present (I can't test it since I don't have a motor).

## Possible issues

On Rasbien, some issues may be solved by not having all packages fully updated.

```
$ sudo apt update
$ sudo apt dist-upgrade
```

A restart may also be required or help.

```
$ sudo shutdown -r now
```

Since opencv and numpy are installed via aptitude, pip shouldn't be necessary. If these packages are installed via pip there might be some resolution errors so you can try [removing all pip packages][rpip] or try to clean up pip manually. Since this uses python 3 and Rasbien defaults to python2, `pip` needs to be replaced with `pip3` wherever relevant.

[rpip]: https://stackoverflow.com/questions/11248073/what-is-the-easiest-way-to-remove-all-packages-installed-by-pip
