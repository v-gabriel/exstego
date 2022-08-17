import os
import matplotlib.pyplot as plot
import cv2
from helpers.enums import FileOriginType, HistogramAnalyzerResults
from helpers.logger import MessageHelper


class HistogramAnalyzer:
    def __init__(self, folder, stegoImgSrc, originalImgSrc):
        self.__identifier = 'HistogramAnalyzer'

        self.folder = folder + '/HistogramAnalysis'
        self.__originalImage = cv2.imread(originalImgSrc)
        self.__stegoImage = cv2.imread(stegoImgSrc)

        self.__results = HistogramAnalyzerResults()

    @property
    def results(self):
        return self.__results

    def __save_histogram(self, img, fileOriginType):
        try:
            MessageHelper.log("Saving histograms...", self.__identifier)

            match fileOriginType:
                case FileOriginType.ORIGINAL.value:
                    filename = 'original'
                case FileOriginType.STEGO.value:
                    filename = 'stego'
                case _:
                    filename = "unknown"

            colour = ('r', 'g', 'b')
            for i, c in enumerate(colour):
                c_hist = cv2.calcHist([img], [i], None, [256], [0, 256])
                plot.plot(c_hist, color=c)
                plot.xlim([0, 256])

            os.makedirs(self.folder, exist_ok=True)
            src = f"{self.folder}/{filename}_histogram.png"
            plot.savefig(src)

            plot.clf()
            plot.cla()

            self.__results.histogram_src[fileOriginType] = src

            MessageHelper.success("Histograms saved successfully.", self.__identifier)
        except Exception as exception:
            MessageHelper.error("Error while saving histograms.", self.__identifier, exception)

    def __compare_histograms(self):
        try:
            MessageHelper.log("Comparing histograms...", self.__identifier)

            histOriginalImage = cv2.calcHist([self.__originalImage], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
            histStegoImage = cv2.calcHist([self.__stegoImage], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])

            histOriginalImage[255, 255, 255] = 0
            histStegoImage[255, 255, 255] = 0
            cv2.normalize(histOriginalImage, histOriginalImage, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            cv2.normalize(histStegoImage, histStegoImage, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

            self.__results.equality_percentage = cv2.compareHist(histOriginalImage, histStegoImage, cv2.HISTCMP_CORREL)

            message = f"Equality percentage: {self.__results.equality_percentage}%"
            text_src = f"{self.folder}/equality_percentage.txt"
            text_file = open(text_src, "w", encoding="utf-8")
            n = text_file.write(message)
            text_file.close()

            MessageHelper.success("Histograms compared successfully.", self.__identifier)
        except Exception as exception:
            MessageHelper.error("Error while comparing histograms.", self.__identifier, exception)

    def analyze(self):
        if self.__stegoImage is not None and self.__originalImage is not None:
            MessageHelper.log("Performing histogram analysis...", self.__identifier)
            try:
                self.__save_histogram(self.__stegoImage, FileOriginType.STEGO.value)
                self.__save_histogram(self.__originalImage, FileOriginType.ORIGINAL.value)
                self.__compare_histograms()

                MessageHelper.success(f"Files analyzed successfully!"
                                   f"\nRoot folder: {self.folder}", self.__identifier)
            except Exception as exception:
                MessageHelper.error("An error has occurred... please try again later", self.__identifier, exception)
        else:
            MessageHelper.log("File(s) not provided... aborting...", self.__identifier)
