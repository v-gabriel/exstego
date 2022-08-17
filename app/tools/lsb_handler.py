import os
import random
from copy import deepcopy
import numpy as np
from PIL import Image
from helpers.enums import ColorType, LSBEmbedPixelOption, LSBHandlerResults
from helpers.logger import MessageHelper


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

        if wanted_percentage is not None:
            if embed_percentage > wanted_percentage:
                bits_to_keep = int(wanted_percentage * self.__total_pixels)
                b_message = b_message[0:bits_to_keep]
                embed_percentage = wanted_percentage
            elif embed_percentage < wanted_percentage:
                embed_percentage = wanted_percentage
                total_pixels_to_cover = int(self.__total_pixels * embed_percentage)
                fill_length = total_pixels_to_cover - len(b_message)
                b_message_fill = f'{random.getrandbits(fill_length):=0{fill_length}b}'
                b_message += b_message_fill

        try:
            MessageHelper.log(f"Performing LSB embedding for {str(embed_percentage*100)}%...", self.__identifier)

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
        MessageHelper.log(f"Performing LSB extraction...", self.__identifier)
        try:
            if colors_to_read is None:
                colors_to_read = [ColorType.RED.value, ColorType.GREEN.value, ColorType.BLUE.value]
            if percentage is None:
                percentage = 1
                MessageHelper.log(f"Extraction percentage not specified.\n"
                                  f"Setting to default: {percentage * 100}%.",
                                  self.__identifier)

            colors = self.__setup_colors(colors_to_read)
            req_bits = int((percentage * self.__total_pixels) + 0.5)

            hidden_bits = ''
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
                            hidden_bits += (bin(self.__array[pixel_index][c])[2:][-1])
                            index += 1
                    else:
                        break
                else:
                    break

            hidden_bits = [hidden_bits[i:i + 8] for i in range(0, len(hidden_bits), 8)]

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

            color_names = []
            for c in colors_to_read:
                color_names.append(c)
            colors_description = "Colors used: " + str(color_names)
            embedding_description = f"Embedding description:{embed_option}"

            MessageHelper.success(f"Extraction for {str(percentage * 100)}% successfully completed!\n"
                                  f"Description: \n{embedding_description}\n{colors_description}\n"
                                  f"Root folder: {self.folder}", self.__identifier)
        except Exception as exception:
            MessageHelper.error("Error while performing LSB extraction.", self.__identifier, exception)

    def destroy_message(self,
                        embed_option=LSBEmbedPixelOption.SEQUENTIAL.value,
                        colors_to_embed=None,
                        destroy_percentage=0.5):
        MessageHelper.log(f"Performing LSB destruction for {str(destroy_percentage*100)}%.", self.__identifier)
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
