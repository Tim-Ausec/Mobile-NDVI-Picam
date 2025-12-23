from picamera2 import Picamera2 
import numpy as np


IMAGE_SIZE = (4608, 2592)
IMAGE_SIZE_2048 = (2048, 1536)
IMAGE_SIZE_1080 = (1080, 720)











#Camera Configure
camNIR = Picamera2(0)
camRGB = Picamera2(1)


configRGB = camRGB.create_video_configuration(
    main={"size": IMAGE_SIZE, "format": "RGB888"}
)
configNIR = camNIR.create_video_configuration(
    main = {"size": IMAGE_SIZE, "format": "GRAY8"}
    
camNIR.configure(configNIR)
camRGB.configure(camRGB)

camRGB.start()
camNIR.start()


#Camera Photo array
#structure array of frame[height][length][R|G|B]
frameRGB = camRGB.capture_array()

#structure array of frame[height][length]
frameNIR = camNIR.capture_array()


#Math to for photo
frameR = frameRGB[:,:,0].astype(np.float32)
frameNIR = frameNIR.astype(np.float32)
ndvi = (frameNIR - frameR) / (frameNIR + frameR)

if np.isnan(ndvi):
    print("Divide by 0")
    return;

h, w = ndvi.shape

    
