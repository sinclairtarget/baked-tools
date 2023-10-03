Hi

Welcome to batch converter - a.k.a "FLAYVA MAYKA 5000!"

This app is designed to help convert files from one codec/container to the other in our Baked Pipeline.

Here are the steps for creating a batch of PRORESes from a batch of EXRs. The same steps can be repeated for the two other flavors this thing can make - as well as for the -DNxHD container re-builder.

1. Navigate to the folder structure named for the conversion you're trying to make.
2. Open it up, and notice the "In" and "Out" folders. This is where you'll place your media and collect it when it's done.
3. Above the in/out folders is a .sh file. This is the script we're running. Copy the full name of the script, including its extension.
4. Go back to the root folder of the app and right click the conversion folder you're trying to use - so for EXRs it would be \1_EXR-PRORES
5. Select "New Terminal at Folder" near the bottom of the drop down.
6. Type ./(paste .sh file name - including .sh bit)
7. Hit enter.

Note: your EXR files must adhere to the following naming convetion: (Folder name).(framenumber).exr - so an example would be ABC_123_1234.1001 - if you have a folder named for the resolution of the exr, you will have to rename. If you have too much frame number padding too, like .0001001, you will need to remove. This is standard for our Staging process anyway!

That's it! You can check progress by reading some of the stuff that pops up. It will show you what shot you're on and what frame it's encoding.
