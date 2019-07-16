#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Convert a PDF into PNG file(s).

For this script to work the 3rd party library 'wand' is required.
    pip install wand
Wand has dependencies on ImageMagick and Ghostscript.

  + ImageMagick 7 is not yet supported so ImageMagick 6 should be
    installed from here: https://sourceforge.net/projects/imagemagick/files/
      + 32-bit: ImageMagick-6.9.9-37-Q16-HDRI-x86-dll
      + 64-bit: ImageMagick-6.9.9-37-Q16-HDRI-x64-dll


    During the installation you will also need to follow the
    instructions listed here:
        http://docs.wand-py.org/en/latest/guide/install.html#install-imagemagick-on-windows


  + GhostScript can be downloaded under the AGPL license from the main
    website and the related python package using pip.
        https://www.ghostscript.com/download.html
        pip install ghostscript


Written By (Last Updated)
    Ali Al-Hakim (30 September 2018)

"""
import os
from wand.image import Image
from wand.exceptions import *


########################################################################
def pdf_to_png(pdf_filepath, pages=None, verbose=False):
    """Convert the pages of a PDF to PNG images.

    PARAMETERS
    ==========
        pdf_filepath: <str>
            The filepath of the PDF to be converted into PNG images.
            All PNG images will be saved in the same directory in a new
            folder  called "png".

        pages: <int> or [list of <int>] or None
            Default/None: Return a PNG image of all pages
            Otherwise, the pages requested will be created:
                If pages=5, a PNG of page 5 will be saved
                If pages=[2,4], a PNG of pages 2 and 4 will be saved
                etc

        verbose: <bool>
            Set to True to display print statements.

    RETURNS
    =======
        Nothing.
        However, if successful PNG images will be created.

    """

    # Make sure the correct filepaths are available
    pdf_filename = os.path.basename(pdf_filepath)
    pdf_directory = os.path.dirname(pdf_filepath)
    png_filename = pdf_filename.replace(".pdf", ".png")
    png_directory = os.path.join(pdf_directory, "png")
    if not os.path.exists(png_directory):
        os.makedirs(png_directory)
    png_filepath = os.path.join(png_directory, png_filename)

    if verbose: print(" > Converting '{}' to PNG images".format(pdf_filename))

    # Use Wand to open the PDF as sequence of images and convert and
    # save these as PNG files.
    try:
        with Image(filename=pdf_filepath, resolution=100) as pdf_img:
            pdf_pages = pdf_img.sequence
            pdf_page_count = len(pdf_pages)

            # If pages is not defined then convert the entire document.
            if pages is None:
                if verbose: print("    - Pages ALL/{}".format(pdf_page_count))
                with pdf_img.convert("png") as converted:
                    converted.save(filename=png_filepath)

            # Otherwise, only convert the defined pages.
            else:
                if type(pages) == int: pages = [pages]
                for page in pages:
                    assert(page > 0), "Invalid page number: {}. Pages must be positive integers.".format(page)
                    assert(page <= pdf_page_count), "Invalid page number: '{}'. {} only has {} pages.".format(page, pdf_filename, pdf_pages)
                    if verbose: print("    - Page {}/{}".format(page, pdf_page_count))

                    # Save the desired PDF pages as PNG files.
                    index = page - 1
                    page_png_filepath = png_filepath.replace(".png", "-p{}.png".format(page))
                    with Image(pdf_pages[index]) as page_img:
                        with page_img.convert("png") as converted:
                            converted.save(filename=page_png_filepath)

    except CorruptImageError as e:
        # In some cases Wand may throw an exception if the PDF format
        # is non-standard (I think). For exampl, the following exceptions
        # seemed to be thrown due to a PDF which had custom sized pages
        #   > wand.exceptions.CorruptImageError: unable to read image data
        #   > TypeError: object of type 'NoneType' has no len()
        # This isn't wholly confirmed but it's clear not all PDFs are
        # opened equally.
        print("ERROR:", e)

    if verbose: print("    - Complete")


def pdf_cover_to_png(pdf_filepath, verbose=False):
    """Convert the first page of a PDF to a PNG image.

    PARAMETERS
    ==========
        pdf_filepath: <str>
            The filepath of the PDF to be converted into PNG images.
            All PNG images will be saved in the same directory in a new
            folder  called "png"

        verbose: <bool>
            Set to True to display print statements..

    RETURNS
    =======
        Nothing.
        However, if successful PNG images will be created.

    """
    pdf_to_png(pdf_filepath, pages=1, verbose=verbose)


########################################################################
if __name__ == "__main__":
    print("Running...")

    PDF_DIRECTORY = os.path.join(os.path.dirname(__file__), "user-guides")
    VERBOSE = True

    # Find all PDF files in PDF_DIRECTORY
    pdf_files = [f for f in os.listdir(PDF_DIRECTORY) if os.path.isfile(os.path.join(PDF_DIRECTORY, f))]
    for filename in pdf_files:
        filepath = os.path.join(PDF_DIRECTORY, filename)
        pdf_cover_to_png(filepath, verbose=VERBOSE)

    print("Complete.")
