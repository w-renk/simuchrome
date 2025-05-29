This command line utility applies an emulation to images taken with a full-spectrum or IR converted digital camera to (kind of) make the images look they were taken with Aerochrome.

[Standalone Windows exe here.](https://github.com/w-renk/simuchrome/releases/tag/v1.0)

Based on the [method proposed by Flickr user jw_wong](https://www.flickr.com/photos/jw_wong/4960099202/) in 2010, which I found out about [from this 2023 video by Jason Kummerfeldt](https://www.youtube.com/watch?v=v5KBQd_DkQw).

The math isn't quite the same, but it's close enough that some light curves/levels adjustments in a photo editor are enough to complete the look. This just saves the effort of manually setting up subtraction and adjustment layers to get to a composited image. If you have a suggestion for improving the math, feel free to open an issue.

If you prefer taking a more hands on approach, Jason's method is pretty straightforward and allows more control and experimentaion during the compositing process. This program just allows you to quickly apply a consistent emulation profile that you can adjust to your camera sensor.

## Input image

Images must be taken on a camera sensitive to infrared light and through a filter (or filter stack) that cuts out wavelengths shorter than ~500 nanometers. A Tiffen Yellow 15 is pretty much perfect for this. You could probably get away with using a Yellow 12 or an Orange 16, but you'd be allowing some blue or cutting some green respectively.

I would recommend shooting in RAW, then adjusting the exposure in your preferred RAW processor and exporting to PNG or BMP. The program internally converts images to bitmaps before performing adjustment, so if you start with a JPEG, any compression artifacts will be baked into the image before it gets compressed again.

Also included is the Darktable style I use before running images through the simuchrome script. It sets the tint to 1.3 and the white balance to 2500K in addition to applying haze removal and the default denoise, hot pixel, and sharpen settings. The camera I use is a Sony a6000, so this style as well as the default settings in the simulation.toml file are tuned for that camera and sensor shot in bright daylight.

## Usage
Python:
```
> pip install -r requirements.txt
> python simuchrome.py infile [--simulation, -s] outfile
```

Executable
```
simuchrome.exe infile [--simulation, -s] outfile
```

`--simulation` or `-s` should be followed by a path to toml file containing custom values for the calculations. It must be in the same format as the included simulation.toml file, or you can edit the values directly in that file and run the program without the -s option. Explanations of the values and their effects on the output image are described in simulation.toml. At a minimum, the RInIrFrac and GInIrFrac values need to be adjusted based on your camera sensor and the exact filter(s) you use.

## Theory

By using an IR sensitive camera and filtering out cyan and shorter wavelengths, you can take an image where the B channel is mostly only capturing infrared light and the R and G channels are capturing a combination of their respective color and IR.

The B value for each pixel is scaled by some amount (RInIrFrac and GInIrFrac) and subtracted from the R and G values. This leaves the R and G channels ideally showing only the color component and none (or little) of the IR component.

The pixel values are then recomposited so that IR data on the input B channel is written to the output R channel, input R is written to output G, and input G is written to output B.

Adjusting the gamma values in the simulation.toml file allows you to balance the brightness of each color channel in the composited image, though this is functionally identical to adjusting curves in a photo editor after the image has been output. Because the gamma adjustments are destructive, if you plan on editing the output image's color, set the gamma values to 1.
