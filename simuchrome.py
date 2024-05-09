import cv2
import numpy
import argparse
import toml

def adjustGamma(image, gamma):
    invGamma = 1.0 / gamma
    table = numpy.array([((i / 255) ** invGamma) * 255 for i in numpy.arange(0,256)]).astype(numpy.uint8)
    return cv2.LUT(image, table)

parser = argparse.ArgumentParser(
    prog="Digichrome",
    description="takes an image captured with an IR sensitive camera and a blue cut filter and replicates the look of the Aerochrome film stock")
parser.add_argument('inFile')
parser.add_argument('-s', '--simulation', help="custom simulation toml file to use instead of the default")
parser.add_argument('outFile')

try:
    args = parser.parse_args()
    
    redIrFrac = 0.0
    greenIrFrac = 0.0
    redGamma = 0.0
    greenGamma = 0.0
    blueGamma = 0.0
    tomlPath = ''
    
    if args.simulation:
        tomlPath = args.simulation
    else:
        tomlPath = 'simulation.toml'
        
    v = toml.load(tomlPath)
    redIrFrac = v['RInIrFrac']
    greenIrFrac = v['GInIrFrac']
    redGamma = v['ROutGamma']
    greenGamma = v['GOutGamma']
    blueGamma = v['BOutGamma']
    
    # read the full spectrum image
    fsBMP = cv2.imread(args.inFile, cv2.IMREAD_COLOR)
    
    # split the full spectrum image into component channels
    # (cv2 represents bitmaps as BGR instead of RGB which is why the 0 channel is B)
    redIn = fsBMP[:,:,2]
    greenIn = fsBMP[:,:,1]
    blueIn = fsBMP[:,:,0]
    
    # the blueIn channel contains only IR (assuming photo was shot with a filter that cuts out wavelengths
    # shorter than about 500-530nm)
    # the redIn and greenIn channels contain R+IR and G+IR respectively
    # simply subtracting the IR data in the blueIn channel from the other two channels produces
    # a reasonable effect, but scaling the amount of the IR channel that gets subtracted and 
    # modifying gamma of each channel can further fine tune the emulation
    # the exact scalars to use for this depend heavily on the camera sensor
    
    # arrays must be cast as signed ints to prevent underflows, conveniently this also undoes
    # python's automatic conversion of the blueIn array to floats when multiplying by a fraction
    redMinusIR = (redIn.astype(numpy.int16) - (blueIn * redIrFrac).astype(numpy.int16))
    # then clamp the values to the u8 range
    redMinusIR = numpy.clip(redMinusIR, 0, 255)
    
    greenMinusIR = (greenIn.astype(numpy.int16) - (blueIn * greenIrFrac).astype(numpy.int16))
    greenMinusIR = numpy.clip(greenMinusIR, 0, 255)
    
    
    
    #IR (blue) becomes R, R becomes G, G becomes B
    
    # apply gamma corections
    redOut = adjustGamma(blueIn, redGamma)
    greenOut = adjustGamma(redMinusIR.astype(numpy.uint8), greenGamma)
    blueOut = adjustGamma(greenMinusIR.astype(numpy.uint8), blueGamma)
    
    # composit image
    imgOut = numpy.zeros(fsBMP.shape)
    
    # imgOut[:,:,0] is the output B channel
    # [:,:,1] is green and [:,:,2] is red
    
    imgOut[:,:,0] = blueOut
    imgOut[:,:,1] = greenOut
    imgOut[:,:,2] = redOut
    
    cv2.imwrite(args.outFile, imgOut)
        
except Exception as e:
    if "No such file or directory: 'simulation.toml'" in str(e):
        print("Could not find simulation.toml")
    print("there was an error: ", e)