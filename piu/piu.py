#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import PyPDF2
from PyPDF2.pdf import ContentStream
from PyPDF2.pdf import TextStringObject


class Piu(object):

    def __init__(self, file_path):
        self.file_path = file_path

    def _get_pages(self):
        pdf = PyPDF2.PdfFileReader(open(self.file_path, "rb"))
        return pdf.pages

    def _read_page_content(self, page):
        content = page["/Contents"].getObject()
        if not isinstance(content, ContentStream):
            content = ContentStream(content, page.pdf)
        return content

    def text(self):
        """
        Return an array of texts.The text of nth page' index is n - 1.
        """
        texts = []
        for page in self._get_pages():
            text = self._extract_text(page)
            texts.append(text)

        return texts

    def _handle_content_stream_operator(self, content):
        # PDF operators
        # https://github.com/galkahana/HummusJS/wiki/Use-the-pdf-drawing-operators#operators-list
        # Tj|TJ: apply the Tj operator, which shows text, on the text string
        text = u""
        for operands, operator in content.operations:
            if operator == "Tj":
                _text = operands[0]
                if isinstance(_text, TextStringObject):
                    text += _text

            # T*: text state operators | text position operators
            elif operator == "T*":
                text += "\n"

            # Quote|DoubleQuote: text showing operations
            elif operator == "'":
                text += "\n"
                _text = operands[0]
                if isinstance(_text, TextStringObject):
                    text += operands[0]
            elif operator == '"':
                _text = operands[2]
                if isinstance(_text, TextStringObject):
                    text += "\n"
                    text += _text
            elif operator == "TJ":
                for i in operands[0]:
                    if isinstance(i, TextStringObject):
                        text += i
            text = self._make_string_space(text)
        return text

    def _extract_text(self, page):
        content = self._read_page_content(page)
        return self._handle_content_stream_operator(content)

    def _make_string_space(self, text):
        text = text or ""
        if not text.endswith(" "):
            text += " "
        return text

    def _invoke_gs(self, cmd_options):
        ghostscript = os.environ.get("GHOSTSCRIPT", "gs")
        print cmd_options
        cmd = "%s %s" % (ghostscript, cmd_options)
        return os.system(cmd)

    def _build_cmd_options(self, src, filename, options):
        # default
        cmd_options = ""
        default_options = {
            "-dNOPAUSE": True,
            "-dPDFFitPage": True,
            "-dTextAlphaBits": 4,
            "-sDEVICE": "jpeg",
            "-dJPEG": 80,
            "-dDEVICEWIDTH": 620,
            "-dDEVICEHEIGHT": 480,
        }
        merged_options = default_options.copy()
        merged_options.update(options)
        for option, value in merged_options.items():
            if value is True:
                cmd_options += "%s " % option
            else:
                cmd_options += "%s=%s " % (option, str(value))
        cmd_options += "-sOutputFile=%s " % filename
        cmd_options += "%s -c quit" % src
        return cmd_options

    def create_images(self, output, index=True, prefix="slide", options={}):

        if not os.path.exists(output):
            os.makedirs(output)

        src = self.file_path
        output = output.rstrip("/")
        filename = "%(output)s/%(prefix)s%%d.jpg" % locals()

        cmd_options = self._build_cmd_options(src, filename, options)
        self._invoke_gs(cmd_options)

        if index:
            relative_path = "%s/" % output
            self._create_index(prefix=relative_path)

    def _create_index(self, filename="index.html", prefix=""):
        SLIDE_TEMPLATE = u'<p class="slide"><img src="{prefix}{src}" alt="{alt}" /></p>'
        out = open(filename, "wt")

        texts = self.text()
        print >> out, "<!doctype html>"
        for i in xrange(0, len(texts)):
            alt = texts[i]  # ALT text for this slide
            params = dict(src=u"slide%d.jpg" % (i + 1), prefix=prefix, alt=alt)
            line = SLIDE_TEMPLATE.format(**params)
            print >> out, line.encode("utf-8")

        out.close()
