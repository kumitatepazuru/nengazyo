import sys

import pyocr
import pyocr.builders


class ocr:
    def __init__(self, lang, builder):
        self.builder = builder
        self.tools = pyocr.get_available_tools()
        if len(self.tools) == 0:
            print("No OCR tool found")
            sys.exit(1)

        self.tool = self.tools[0]
        print("Will use tool '%s'" % (self.tool.get_name()))

        langs = self.tool.get_available_languages()
        print("Available languages: %s" % ", ".join(langs))
        self.lang = lang
        print("Will use lang '%s'" % self.lang)

    def ocr(self, imgdata):
        if self.builder == "digit":
            txt = self.tool.image_to_string(
                imgdata,
                lang=self.lang,
                builder=pyocr.builders.DigitBuilder(tesseract_layout=13))
        elif self.builder == "text":
            txt = self.tool.image_to_string(
                imgdata,
                lang=self.lang,
                builder=pyocr.builders.TextBuilder(tesseract_layout=6))
        else:
            raise IndexError("変数builderにはdigitまたはtextが入ります。")
        return txt
