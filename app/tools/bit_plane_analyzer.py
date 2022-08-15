import os
from PIL import Image
import matplotlib.pyplot as plot
import cv2
import numpy as np
from helpers.enums import BPCSAnalyzerResults, ColorType, FileOriginType
from helpers.logger import MessageHelper


class BitPlaneAnalyzer:
    def __init__(self, folder, stegoImageSrc, originalImageSrc=None):
        self.__identifier = "BitPlaneAnalyzer"

        self.stegoImageSrc = stegoImageSrc
        self.originalImageSrc = originalImageSrc

        self.folder = folder + '/BitPlaneAnalysis'

        self.__results = BPCSAnalyzerResults()

    @property
    def results(self):
        return self.__results

    def __save_bit_planes(self, image, dest, colorType, fileOriginType, bit_planes_to_split=None):
        if bit_planes_to_split is None:
            bit_planes_to_split = [1, 2, 3, 4, 5, 6, 7, 8]
        try:
            MessageHelper.log(f"Saving bit planes..\n"
                              f"Color file_type: {colorType}\n"
                              f"Planes: {bit_planes_to_split}",
                              self.__identifier)
            match colorType:
                case ColorType.BLUE.value:
                    filename = dest + '/blue'
                case ColorType.RED.value:
                    filename = dest + '/red'
                case ColorType.GREEN.value:
                    filename = dest + '/green'
                case _:
                    raise Exception("Invalid color channel file_type.")

            plane_srcs = []
            row, column = image.shape
            plane = np.zeros((row, column, 8), dtype=np.uint8)
            for p in bit_planes_to_split:
                plane[:, :, p - 1] = 2 ** (p - 1)
            for p in bit_planes_to_split:
                temp = cv2.bitwise_and(image, plane[:, :, p - 1]) * 255
                src = filename + str(p) + 'plane.png'
                plane_srcs.append(src)
                cv2.imwrite(src, temp)

            self.__results.bit_planes_per_channel[fileOriginType][colorType] = plane_srcs

            MessageHelper.success(f"Planes saved successfully\n"
                                  f"Color file_type: {colorType}\n"
                                  f"Planes: {bit_planes_to_split}",
                                  self.__identifier)
        except Exception as exception:
            MessageHelper.error("Error while saving bit planes.\n"
                                f"Color file_type: {colorType}\n",
                                self.__identifier,
                                exception)

    def separate_channels(self, file_origin_type, bit_planes_to_split=None, color_channels=None):
        if color_channels is None:
            color_channels = [ColorType.RED.value, ColorType.GREEN.value, ColorType.BLUE.value]
        if bit_planes_to_split is None:
            bit_planes_to_split = [1, 2, 3, 4, 5, 6, 7, 8]

        match file_origin_type:
            case FileOriginType.ORIGINAL.value:
                destination = self.folder + '/' + 'Original'
                image = cv2.imread(self.originalImageSrc)
            case FileOriginType.STEGO.value:
                destination = self.folder + '/' + 'Stego'
                image = cv2.imread(self.stegoImageSrc)
            case _:
                raise Exception("Invalid file origin.")

        try:
            MessageHelper.log(f"Separating color channels...\n"
                              f"Color channels: {color_channels}\n"
                              f"File file_type: {file_origin_type}",
                              self.__identifier)

            r = image.copy()
            g = image.copy()
            b = image.copy()

            for channel in color_channels:
                match channel:
                    case ColorType.BLUE.value:
                        b[:, :, 2] = 0
                        b[:, :, 1] = 0
                        temp_destination = destination + '/Blue'
                        os.makedirs(temp_destination, exist_ok=True)
                        filename = temp_destination + '/blue-channel.png'
                        cv2.imwrite(filename, b)
                        self.__save_bit_planes(cv2.imread(filename, 0),
                                               temp_destination,
                                               ColorType.BLUE.value,
                                               file_origin_type,
                                               bit_planes_to_split)
                    case ColorType.RED.value:
                        r[:, :, 1] = 0
                        r[:, :, 0] = 0
                        temp_destination = destination + '/Red'
                        os.makedirs(temp_destination, exist_ok=True)
                        filename = temp_destination + '/red-channel.png'
                        cv2.imwrite(filename, r)
                        self.__save_bit_planes(cv2.imread(filename, 0),
                                               temp_destination,
                                               ColorType.RED.value,
                                               file_origin_type,
                                               bit_planes_to_split)

                    case ColorType.GREEN.value:
                        g[:, :, 0] = 0
                        g[:, :, 2] = 0
                        temp_destination = destination + '/Green'
                        os.makedirs(temp_destination, exist_ok=True)
                        filename = temp_destination + '/green-channel.png'
                        cv2.imwrite(filename, g)
                        self.__save_bit_planes(cv2.imread(filename, 0),
                                               temp_destination,
                                               ColorType.GREEN.value,
                                               file_origin_type,
                                               bit_planes_to_split)

            MessageHelper.success(f"Channels separated successfully.\n"
                                  f"Color channels: {color_channels}\n"
                                  f"File file_type: {file_origin_type}",
                                  self.__identifier)
        except Exception as exception:
            MessageHelper.error(f"Error while separating color channels.\n"
                                f"Color channels: {color_channels}\n"
                                f"Bit planes {bit_planes_to_split}",
                                self.__identifier,
                                exception)

    def overlap_bit_planes(self, file_origin_type, bit_planes_to_overlap=None):
        if bit_planes_to_overlap is None:
            bit_planes_to_overlap = [1, 2, 3, 4, 5, 6, 7, 8]

        for plane in bit_planes_to_overlap:
            if plane > 8:
                plane = 8

        match file_origin_type:
            case FileOriginType.ORIGINAL.value:
                destination = self.folder + '/' + 'Original'
                image = Image.open(self.originalImageSrc)
            case FileOriginType.STEGO.value:
                destination = self.folder + '/' + 'Stego'
                image = Image.open(self.stegoImageSrc)
            case _:
                raise Exception("Invalid file.")

        destination += '/BitPlanesOverlap'

        try:
            MessageHelper.log(f"Overlapping bit planes...\n"
                              f"Bit planes: {bit_planes_to_overlap}", self.__identifier)

            data = np.array(image)

            bit_planes_to_keep = format(int('00000000', 2), '08b')[0:8]
            for plane in bit_planes_to_overlap:
                to_left = 8 - plane
                from_right = to_left + 1
                bit_planes_to_keep = bit_planes_to_keep[:to_left] + '1' + bit_planes_to_keep[from_right:8]

            bit_planes_to_keep = bit_planes_to_keep.lstrip('0')
            print(bit_planes_to_keep)
            binOp = format(int(bit_planes_to_keep, 2), '08b')[0:8]
            intOp = int(binOp, 2)
            print(intOp)
            extracted = (data[..., 0] ^ data[..., 1] ^ data[..., 2]) & intOp

            fig = plot.imshow(extracted)
            plot.axis('off')
            fig.axes.get_xaxis().set_visible(False)
            fig.axes.get_yaxis().set_visible(False)

            os.makedirs(destination, exist_ok=True)
            src = destination + '/bit-planes-overlap.png'
            plot.savefig(src, bbox_inches='tight', pad_inches=0)

            self.__results.planes_overlap_image[file_origin_type] = src

            MessageHelper.success(f"Bit planes overlapped successfully.\n"
                                  f"Bit planes: {bit_planes_to_overlap}",
                                  self.__identifier)
        except Exception as exception:
            MessageHelper.error(f"Error while overlapping bit planes\n"
                                f"Bit planes: {bit_planes_to_overlap}",
                                self.__identifier,
                                exception)
