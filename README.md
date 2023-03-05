# Baked Tools
A collection of scripts for interacting with the Shotgrid Python API.

## Instructions (for End Users)
### Things You Need
You need the program itself installed on your computer. This should just be a
file called `baked-tools.pex`.

You also need the Baked Tools API key. Someone needs to give this to you if you
don't have it already.

### Running the Program
To invoke the program, you need to use a terminal emulator application. On
MacOS, there is a terminal emulator installed by default called _Terminal_.

You need to open your terminal emulator, then navigate to the directory where
you have your media to upload. Make sure the file `baked-tools.pex` is either
in your `PATH` (see
[here](https://askubuntu.com/questions/109381/how-to-add-path-of-a-program-to-path-environment-variable))
or available in the directory where you have your media files.

You can them upload your media by invoking, for example, the following:

```
$ SHOTGRID_API_KEY=xxx ./baked-tools.pex upload "Python API Test Project" *.mp4
```

You must provide the API key as shown in the above command. Replace `xxx` with
the actual API key.

It can be inconvenient to specify the API key every time you run the program,
so another option is to export the API key to your environment. See
[here](https://askubuntu.com/questions/58814/how-do-i-add-environment-variables)
for instructions on how to do that.

### Getting More Help
You can get additional help about how to run the program by invoking:

```
$ ./baked-tools.pex --help
```

## Instructions (for Developers)
Create a virtual environment using a tool like `virtualenv`.

The Python dependencies are managed by `pip-tools`. Install `pip-tools` into
your virtual environment with `pip install pip-tools`.

You can then install the remaining dependencies using `pip-sync
requirements.txt dev-requirements.txt`.

### Building for Release
You build a `.pex` executable by running the `build.sh` script.
