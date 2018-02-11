__author__ = 'imuchnik'

import time

from PIL import Image, ImageChops, ImageOps, ImageStat, ImageFilter
import math, operator

class ImageUtils:

    def findOffset(self, img1, img2):

        im1_first_pixel= self.findFirstBlackPixel(img1)
        im2_first_pixel= self.findFirstBlackPixel(img2)

        offset =((im1_first_pixel[0]-im2_first_pixel[0]), im1_first_pixel[1]-im2_first_pixel[1])

        return offset


    def findFirstBlackPixel(self, img):
        for y in range(0, img.size[1]):
            for x in range(0, img.size[0]):
                p1 =img.getpixel((x,y))
                if p1 == 0:
                    img_first_pixel =(x,y)
                    return img_first_pixel


    def add_images(self, im1, im2):
        offset= self.findOffset(im1, im2)

        if offset==(0,0):
            return ImageChops.add(im1, im2)
        else:
            return ImageChops.add(im1, ImageChops.offset(im2,offset[0], offset[1]))

    def diff_images(self, im1, im2):
        offset= self.findOffset(im1, im2)

        if offset==(0,0):
            return ImageChops.difference(im1, im2)
        else:
            return ImageChops.difference(im1, ImageChops.offset(im2,offset[0], offset[1]))

    def isEqual(self, im1, im2):
        # offset =self.findOffset(im1, im2)
        # newImage= ImageChops.offset(im2,offset[0], offset[1])
        inverted =self.invertGrayScaleImage(im1)
        sumOfTwo = ImageChops.add(inverted, im2)

        if len(list(sumOfTwo.getcolors()))>1:
            if list(sumOfTwo.getcolors())[0][1] ==0:

                return list(sumOfTwo.getcolors())[0][0]<155
            elif list(sumOfTwo.getcolors())[1][1] ==0:
                return list(sumOfTwo.getcolors())[1][0]<155
        else:
            return list(sumOfTwo.getcolors())[0][1] ==255

    def invertGrayScaleImage(self, image):
        inverted = Image.new("1", image.size, "white")
        for x in range(0, image.size[1]):
            for y in range(0, image.size[0]):
                p1 = image.getpixel((x, y))
                if (p1 == 0):
                    inverted.putpixel((x, y), 255)
                else:
                    inverted.putpixel((x, y), 0)

        return inverted

    def compareImages(self, img1, img2):
        common = Image.new("1", img1.size, "white")

        delta = Image.new("1", img1.size, "white")
        for x in range(0, common.size[1]):
            for y in range(0, common.size[0]):
                p1 = img1.getpixel((x, y))
                p2 = img2.getpixel((x, y))
                if (p1 == 0 and p2 == 0):
                    common.putpixel((x, y), 0)

                elif p1 == 255 and p2 == 255:
                    common.putpixel((x, y), 255)

                else:

                    delta.putpixel((x, y), 0)

        return common, delta
