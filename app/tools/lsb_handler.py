import os
import random
from copy import deepcopy
from datetime import date
from gettext import gettext

import cv2
import numpy as np
import shortuuid
from PIL import Image
from helpers.enums import ColorType, LSBEmbedPixelOption, LSBHandlerResults
from helpers.logger import MessageHelper


# ====================================================================================================
# -> Perform LSB steganography <-
#   - hide message, read LSBs or destroy a hidden message

# ! Notes
# 2 embed options:
#   - SEQUENTIAL: embedding starts from beginning to end, dependant on message length
#   - SCATTER: embedding starts from beginning, certain pixels are skipped (step embedding)
# percentage parameter determines how much % of the image will be embedded over
# if the message size is less than wanted embedding size, randomized bits will be added to message end
# ====================================================================================================


class LSBHandler:
    def __init__(self,
                 folder,
                 src,
                 ):
        self.__identifier = 'LSBHandler'
        self.__src = src

        self.__iteration = 0
        self.folder = folder + '/LSBHandler'

        self.__img = Image.open(self.__src, 'r')
        if self.__img.mode == 'RGB':
            self.__n = 3
        elif self.__img.mode == 'RGBA':
            self.__n = 4
        self.__width, self.__height = self.__img.size

        self.__array = np.array(list(self.__img.getdata()))
        self.__total_pixels = self.__array.size // self.__n

        self.__results = LSBHandlerResults()

    @property
    def results(self):
        return self.__results

    def __setup_colors(self, colors_to_filter):
        colors = []
        for color in colors_to_filter:
            match color:
                case ColorType.RED.value:
                    colors.append(0)
                case ColorType.GREEN.value:
                    colors.append(1)
                case ColorType.BLUE.value:
                    colors.append(2)
                case _:
                    raise Exception("Invalid color(s) specified")
        return colors

    def __perform_stegging(self,
                           b_message,
                           embed_option=LSBEmbedPixelOption.SEQUENTIAL.value,
                           colors_to_embed=None,
                           percentage=None):

        if colors_to_embed is None:
            colors_to_read = [ColorType.RED.value, ColorType.GREEN.value, ColorType.BLUE.value]

        colors = self.__setup_colors(colors_to_embed)
        array = deepcopy(self.__array)
        req_bits = len(b_message)

        index = 0
        for p in range(self.__total_pixels):
            match embed_option:
                case LSBEmbedPixelOption.SCATTER.value:
                    pixel_index = int(p * float(1 / (percentage / len(colors))))
                case LSBEmbedPixelOption.SEQUENTIAL.value:
                    pixel_index = p
                case _:
                    raise Exception("Invalid embedding option. Please retry or reset parameters.")
            if index < req_bits:
                if pixel_index < self.__total_pixels:
                    for c in colors:
                        array[pixel_index][c] = int(
                            format(
                                (array[pixel_index][c]), '08b')[0:7] +
                            b_message[index], 2)
                        index += 1
                        if index >= len(b_message):
                            break
                else:
                    break
            else:
                break

        return array

    def hide_message(self,
                     message,
                     embed_option=LSBEmbedPixelOption.SEQUENTIAL.value,
                     colors_to_embed=None,
                     wanted_percentage=None):

        b_message = ''.join([format(ord(i), "08b") for i in message])
        embed_percentage = float(float(len(b_message)) / float(self.__total_pixels))

        print(f"Total pixels: {self.__total_pixels}")
        print(f"Bits to cover: {len(b_message)}")
        print(f"Wanted percentage: {wanted_percentage}")
        print(f"Covered percentage: {embed_percentage}")

        if wanted_percentage is not None:
            if embed_percentage > wanted_percentage:
                bits_to_keep = int(wanted_percentage * self.__total_pixels)
                print(bits_to_keep)
                b_message = b_message[0:bits_to_keep]
                embed_percentage = wanted_percentage
            elif embed_percentage < wanted_percentage:
                embed_percentage = wanted_percentage
                total_pixels_to_cover = int(self.__total_pixels * embed_percentage)
                fill_length = total_pixels_to_cover - len(b_message)
                b_message_fill = f'{random.getrandbits(fill_length):=0{fill_length}b}'
                b_message += b_message_fill

        print(len(b_message))
        print(f"New covered percentage: {float(len(b_message) / self.__total_pixels)}")

        try:
            MessageHelper.log(f"Performing LSB embedding for {str(embed_percentage)}.", self.__identifier)

            array = self.__perform_stegging(b_message, embed_option, colors_to_embed, embed_percentage)
            self.__array = deepcopy(array)

            os.makedirs(self.folder, exist_ok=True)
            array = array.reshape(self.__height, self.__width, self.__n)
            enc_img = Image.fromarray(array.astype('uint8'), self.__img.mode)

            src = f"{self.folder}/hidden_{str(embed_percentage * 100)}percent.png"
            enc_img.save(src)
            self.__results.hidden_image_source = src

            color_names = []
            for c in colors_to_embed:
                color_names.append(c)
            colors_description = f"Colors used: {str(color_names)}"
            embedding_description = f"Embedding description: {embed_option}"

            MessageHelper.success(f"Stegging for {str(embed_percentage * 100)}% successfully completed!\n"
                                  f"Description: \n{embedding_description}\n{colors_description}\n"
                                  f"Root folder: {self.folder}", self.__identifier)
        except Exception as exception:
            MessageHelper.error("Error while LSB message hiding.", self.__identifier, exception)

    def extract_message(self,
                        colors_to_read=None,
                        embed_option=LSBEmbedPixelOption.SEQUENTIAL.value,
                        percentage=None):
        MessageHelper.log(f"Performing LSB extraction.", self.__identifier)
        try:
            if colors_to_read is None:
                colors_to_read = [ColorType.RED.value, ColorType.GREEN.value, ColorType.BLUE.value]
            if percentage is None:
                percentage = 1
                MessageHelper.log(f"Extraction percentage not specified.\n"
                                  f"Setting to default: {percentage * 100}%.",
                                  self.__identifier)

            colors = self.__setup_colors(colors_to_read)
            #req_bits = int(((percentage / len(colors)) * self.__total_pixels) + 0.5)
            req_bits = int((percentage * self.__total_pixels) + 0.5)

            print(f"Req: ({percentage}/{len(colors)})*{self.__total_pixels}={req_bits}")
            print(percentage)

            hidden_bits = ''
            index = 0
            for p in range(self.__total_pixels):
                match embed_option:
                    case LSBEmbedPixelOption.SCATTER.value:
                        pixel_index = int(p * float(1 / (percentage / len(colors))))
                        #print(pixel_index)
                    case LSBEmbedPixelOption.SEQUENTIAL.value:
                        pixel_index = p
                        #print(pixel_index)
                    case _:
                        raise Exception("Invalid embedding option. Please retry or reset parameters.")
                if index < req_bits:
                    if pixel_index < self.__total_pixels:
                        for c in colors:
                            hidden_bits += (bin(self.__array[pixel_index][c])[2:][-1])
                            index += 1
                            # if req_bits >= len(hidden_bits):
                            #     break
                    else:
                        break
                else:
                    break

            # hidden_bits = ""
            # for p in range(self.__total_pixels):
            #     match embed_option:
            #         case LSBEmbedPixelOption.SCATTER:
            #             pixel_index = int(p * float(1 / percentage))
            #             if pixel_index >= len(self.__array):
            #                 break
            #             else:
            #                 for c in colors:
            #                     hidden_bits += (bin(self.__array[pixel_index][c])[2:][-1])
            #         case LSBEmbedPixelOption.SEQUENTIAL:
            #             for c in colors:
            #                 hidden_bits += (bin(self.__array[p][c])[2:][-1])
            #                 current_percentage = len(hidden_bits) / self.__total_pixels
            #                 if current_percentage >= percentage:
            #                     break
            #             current_percentage = len(hidden_bits) / self.__total_pixels
            #             if current_percentage >= percentage:
            #                 break
            #         case _:
            #             raise Exception("Invalid embedding option. Please retry or reset parameters.")

            hidden_bits = [hidden_bits[i:i + 8] for i in range(0, len(hidden_bits), 8)]
            #print(hidden_bits)

            message = ""
            for i in range(len(hidden_bits)):
                message += chr(int(hidden_bits[i], 2))

            self.__results.extracted_text = message

            destination = self.folder
            filename = '/extracted_data.txt'
            os.makedirs(destination, exist_ok=True)

            text_file = open(destination + filename, "w", encoding="utf-8")
            n = text_file.write(message)
            text_file.close()
        except Exception as exception:
            MessageHelper.error("Error while performing LSB extraction.", self.__identifier, exception)

    def destroy_message(self,
                        embed_option=LSBEmbedPixelOption.SEQUENTIAL.value,
                        colors_to_embed=None,
                        destroy_percentage=0.5):
        MessageHelper.log(f"Performing LSB destruction for {str(destroy_percentage)}.", self.__identifier)
        try:
            if destroy_percentage > 1:
                destroy_percentage = 1
            if destroy_percentage < 0:
                raise Exception("Invalid percentage. Use values from [0, 1].")

            length = int(self.__total_pixels * destroy_percentage) * len(colors_to_embed)
            b_message = f'{random.getrandbits(length):=0{length}b}'

            array = self.__perform_stegging(b_message, embed_option, colors_to_embed, destroy_percentage)
            self.__array = deepcopy(array)

            os.makedirs(self.folder, exist_ok=True)
            array = deepcopy(self.__array)
            array = array.reshape(self.__height, self.__width, self.__n)
            enc_img = Image.fromarray(array.astype('uint8'), self.__img.mode)

            src = f"{self.folder}/destroyed_{str(destroy_percentage * 100)}percent.png"
            enc_img.save(src)

            self.__results.destroyed_image_source = src

            color_names = []
            for c in colors_to_embed:
                color_names.append(c)
            colors_description = "Colors used: " + str(color_names)
            embedding_description = f"Embedding description:{embed_option}"

            MessageHelper.success(f"Stegging for {str(destroy_percentage * 100)}% successfully completed!\n"
                               f"Description: \n{embedding_description}\n{colors_description},\n"
                               f"Root folder: {self.folder}", self.__identifier)
        except Exception as exception:
            MessageHelper.error("Error while performing LSB destruction.", self.__identifier, exception)


# def replace_pallete(imageSrc):
#     img = cv2.imread(imageSrc, cv2.IMREAD_GRAYSCALE)
#
#     folder = baseFolder + "/VisualAttacks/ReplacementPallete"
#     os.makedirs(folder, exist_ok=True)
#
#     cv2.imwrite(folder + "/gray.png", img)
#
#     for i in range(len(img)):
#         for j in range(len(img[i])):
#             if img[i][j] % 2 == 0:
#                 img[i][j] = 0
#             else:
#                 img[i][j] = 255
#
#     cv2.imwrite(folder + "/filtered.png", img)


# def get_text(fn):
#     file = open(fn, 'r')
#     return ''.join([line for line in file])
#
#
# fileSrc = 'D:\\Program Files\\Steganography\\ExstegoV02\\resources\\duck.jpg'
# src2 = "D:\\Program Files\\Steganography\\ExstegoV02\\resources\\white_duck.jpg"
#
# today = date.today()
# time = today.strftime("%b_%d_%Y")
# baseFolder = '../ATTACKS' + '/' + time + '__' + shortuuid.ShortUUID().uuid().title()
#
# dls = LSBHandler(baseFolder, fileSrc)
#
# text_src = '../resources/to_hide.txt'
# hidden_text = f"{get_text(text_src)}"
#print(hidden_text)

#dls.hide_message(hidden_text, LSBEmbedPixelOption.SEQUENTIAL, [ColorType.BLUE], 0.0001)
# dls.extract_message([ColorType.RED], LSBEmbedPixelOption.SEQUENTIAL, 0.0000025680328066191043)
#dls.extract_message([ColorType.BLUE], LSBEmbedPixelOption.SEQUENTIAL, 0.0006)
#dls.destroy_message(LSBEmbedPixelOption.SEQUENTIAL, [ColorType.BLUE, ColorType.GREEN, ColorType.RED], 0.5)
#dls.extract_message([ColorType.BLUE], LSBEmbedPixelOption.SEQUENTIAL, 0.0001)

# replace_pallete(src2)