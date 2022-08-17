import os
import pyexiv2
import shortuuid
from helpers.enums import MetadataTypes, MetadataHandlerResults, MetadataFileChangeType
from helpers.logger import MessageHelper


class MetadataHandler:
    def __init__(self, folder, src):
        self.__identifier = 'MetadataHandler'

        with open(fr'{src}', 'rb+') as f:
            self.__image = pyexiv2.ImageData(f.read())

        self.folder = folder + '/MetadataHandler'

        self.__src = src
        self.__results = MetadataHandlerResults()

    @property
    def results(self):
        return self.__results

    def scramble_tags(self, image=None):
        try:
            MessageHelper.log(f"Scrambling tags...", self.__identifier)

            if image is None:
                with open(fr'{self.__src}', 'rb+') as f:
                    image = pyexiv2.ImageData(f.read())

            xmpTags = image.read_xmp()
            exifTags = image.read_exif()
            iptcTags = image.read_iptc()
            comment = image.read_comment()

            for key in xmpTags:
                change = {key: shortuuid.ShortUUID().uuid().title()}
                image.modify_xmp(change)

            for key in exifTags:
                change = {key: shortuuid.ShortUUID().uuid().title()}
                image.modify_exif(change)

            for key in iptcTags:
                change = {key: shortuuid.ShortUUID().uuid().title()}
                image.modify_iptc(change)

            change = shortuuid.ShortUUID().uuid().title()
            image.modify_comment(change)

            self.results.destroyed_tags = self.__read_tags(
                image=image,
                file_type=MetadataFileChangeType.DESTROYED.value
            )
            self.results.original_tags = self.__read_tags()
            self.__save_image(MetadataFileChangeType.DESTROYED.value, image)

            MessageHelper.success(f"Tags scrambled.", self.__identifier)
        except Exception as exception:
            MessageHelper.error("Error while scrambling tags.", self.__identifier, exception)

    def alter_tags(self, dict=None):
        try:
            MessageHelper.log(f"Altering tags {dict}...", self.__identifier)

            with open(fr'{self.__src}', 'rb+') as f:
                image = pyexiv2.ImageData(f.read())

            altered_keys = []

            for key in dict:
                tagComponents = key.split('.')
                value = dict[key]

                if tagComponents[0] == 'Exif':
                    image.modify_exif({key: value})
                elif tagComponents[0] == 'Xmp':
                    image.modify_xmp({key: value})
                elif tagComponents[0] == 'Iptc':
                    image.modify_iptc({key: value})
                elif tagComponents[0] == 'Comment':
                    image.modify_comment(value)
                else:
                    raise Exception(f"Invalid key provided. Skipping key: {key}")

                altered_keys.append(key)

            self.__results.edited_tags = self.__read_tags(
                image=image,
                file_type=MetadataFileChangeType.ALTERED.value
            )
            self.__results.original_tags = self.__read_tags(keys_to_read=altered_keys)
            self.__save_image(
                MetadataFileChangeType.ALTERED.value,
                image
            )

            MessageHelper.success(f"Tags {altered_keys} altered.", self.__identifier)
        except Exception as exception:
            MessageHelper.error("Error while altering tag.", self.__identifier, exception)

    def read_tags(self, keys_to_read=None):
        self.results.original_tags = self.__read_tags(keys_to_read=keys_to_read)
        self.__save_image(
            MetadataFileChangeType.ORIGINAL.value,
            self.__image
        )

    def __read_tags(self, image=None, keys_to_read=None, file_type=MetadataFileChangeType.ORIGINAL.value):
        try:
            if keys_to_read and len(keys_to_read) != 0:
                message = f"[{file_type}] Reading tags: {keys_to_read}..."
            else:
                message = f"[{file_type}] Reading all tags..."
            MessageHelper.log(message, self.__identifier)

            if image is None:
                with open(fr'{self.__src}', 'rb+') as f:
                    image = pyexiv2.ImageData(f.read())

            xmpTags: dict = {}
            exifTags: dict = {}
            iptcTags: dict = {}
            comment = ''

            if keys_to_read and len(keys_to_read) != 0:
                for key in keys_to_read:
                    tagComponents = key.split('.')
                    try:
                        if tagComponents[0] == 'Exif':
                            xmpTags[key] = image.read_exif()[key]
                        elif tagComponents[0] == 'Xmp':
                            exifTags[key] = image.read_xmp()[key]
                        elif tagComponents[0] == 'Iptc':
                            iptcTags[key] = image.read_iptc()[key]
                        elif tagComponents[0] == 'Comment':
                            comment = image.read_comment(key)
                        else:
                            raise Exception(f"Non existing key. Please check your input or pick another key.")
                    except Exception as exception:
                        MessageHelper.error(f"[{file_type}] Error while reading tag: {key}.", self.__identifier, exception)
            else:
                xmpTags = image.read_xmp()
                exifTags = image.read_exif()
                iptcTags = image.read_iptc()
                comment = image.read_comment()

            tags = {
                MetadataTypes.XMP.value: xmpTags,
                MetadataTypes.EXIF.value: exifTags,
                MetadataTypes.IPTC.value: iptcTags,
                MetadataTypes.COMMENT.value: comment
            }

            no_tags_found = "None found.\n\n"

            formatted_tags = {}
            for tag_type in MetadataTypes:
                temp = ''
                title = f"{tag_type.value}: \n\n"
                if tag_type.value != MetadataTypes.COMMENT.value:
                    for tag_key in tags[tag_type.value]:
                        temp += f"{tag_key}: {tags[tag_type.value][tag_key]}\n"
                else:
                    temp += f"{tags[tag_type.value]}"
                if temp == '':
                    temp = f"{title}\n{no_tags_found}\n"
                else:
                    temp = f"{title}{temp}\n"
                formatted_tags[tag_type.value] = temp

            tagsDict = {MetadataTypes.XMP.value: formatted_tags[MetadataTypes.XMP.value],
                        MetadataTypes.EXIF.value: formatted_tags[MetadataTypes.EXIF.value],
                        MetadataTypes.IPTC.value: formatted_tags[MetadataTypes.IPTC.value],
                        MetadataTypes.COMMENT.value: formatted_tags[MetadataTypes.COMMENT.value]}

            MessageHelper.success(f"[{file_type}] Tags read.", self.__identifier)
            return tagsDict
        except Exception as exception:
            MessageHelper.error(f"[{file_type}] Error while reading tags.", self.__identifier, exception)

    def __save_image(self, change_type, image=None):
        try:
            MessageHelper.log(f"[{change_type}] Saving image...", self.__identifier)

            if image is None:
                with open(fr'{self.__src}', 'rb+') as f:
                    image = pyexiv2.ImageData(f.read())
                    change_type = MetadataFileChangeType.ORIGINAL.value

            os.makedirs(self.folder, exist_ok=True)

            img_src = f"{self.folder}/{change_type}_metadata.png"
            with open(img_src, "wb") as newFile:
                newFile.write(image.get_bytes())

            tags_dict = self.__read_tags(image)
            text_src = f'{self.folder}/{change_type}_tags.txt'

            tags = ''
            for e in MetadataTypes:
                tags += tags_dict[e.value]

            text_file = open(text_src, "w", encoding="utf-8")
            n = text_file.write(tags)
            text_file.close()

            MessageHelper.success(f"Image saved.", self.__identifier)
        except Exception as exception:
            MessageHelper.error("Error while saving image.", self.__identifier, exception)
