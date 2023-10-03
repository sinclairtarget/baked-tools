# Baked Tools
A collection of scripts for interacting with the Shotgrid Python API.

## Instructions (for End Users)
### Things You Need
You need the program itself as a file called `baked-tools.pex`. You should
download this to your `Downloads` folder.

You also need a Shotgrid API key. Someone needs to give this to you if you
don't have it already.

### First Time Setup
If you haven't run the program before, there are a few things you need to do to
get it set up on your computer.

The program needs to be run from a terminal emulator. On MacOS, there is a
terminal emulator installed by default called _Terminal_.

Open the _Terminal_ application. Then enter the following commands, paying
careful attention to the different kinds of quotation marks and replacing
`<your api key here>` with the Shotgrid AIP key.

```
$ mkdir ~/bin
$ cp ~/Downloads/baked-tools.pex ~/bin
$ chmod 755 ~/bin/baked-tools.pex
$ echo 'export PATH=~/bin:$PATH' >> ~/.bashrc
$ echo "export SHOTGRID_API_KEY=$(printf "%q" '<your api key here>')" >> ~/.bashrc
```

Once you've done this, close the terminal window and create a new one. Now you
should be good to go.

### Running the Program
You can upload your media by invoking, for example, the following:

```
$ baked-tools.pex upload "Python API Test Project" *.mp4
```

This will upload all of the `.mp4` files in the current directory to the
project named `Python API Test Project`.

If you just want to upload one or two files, you can do that too:

```
$ baked-tools.pex upload "Python API Test Project" TTD_001_0010.mp4 TTD_001_0020.mp4
```

### Getting More Help
You can get additional help about how to run the program by invoking:

```
$ baked-tools.pex --help
```

## Instructions (for Developers)
Create a virtual environment using a tool like `virtualenv`.

The Python dependencies are managed by `pip-tools`. Install `pip-tools` into
your virtual environment with `pip install pip-tools`.

You can then install the remaining dependencies using `pip-sync
requirements.txt dev-requirements.txt`.

### Building for Release
You build a `.pex` executable by running the `build.sh` script.
