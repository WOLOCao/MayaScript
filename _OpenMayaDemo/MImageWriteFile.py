import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.api.OpenMayaRender as omr

# NOTE 如果裁剪区域超过原图范围则限制到原图的边界上
width = 400
height = 400

# NOTE https://groups.google.com/forum/#!topic/python_inside_maya/Q9NuAd6Av20
pixels = bytearray(width*height*4)
for w in range(width):
    for h in range(height):
        pos = (w+h*width)*4
        # NOTE 这里加数字代表当前像素下 RGBA 四个通道的值
        pixels[pos+0] = 255
        pixels[pos+1] = 255
        pixels[pos+2] = 255
        pixels[pos+3] = 255

# NOTE 返回裁剪的 Image
img = om.MImage()
img.setPixels(pixels, width, height)

img.writeToFile(r'C:\Users\timmyliang\Desktop\FX\test\1.tif', 'tif')