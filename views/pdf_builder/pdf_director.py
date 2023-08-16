import os
import json
from snap.views.pdf_builder.pdf_old_template import Old_Template_Builder
from snap.views.pdf_builder.pdf_new_template import New_Template_Builder
from snap.views.pdf_builder.fill_pdf import PDF_Form_Content, fill_form
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
import bpy
from snap import sn_utils

class PDF_Director:
    """Call the steps for building the .pdf files with different styles.

    Attributes:
        form_info (dict): Dictionary with the data for the form.
        form_paths (dict): Dictionary with the paths of the templates.
        path (str): Path where the .pdf file will be save,
                    include directory, name and '.pdf'.
        print_paper_size (str): Name of the paper format,
                    example: 'LEGAL'
        images (list): list of str with the paths of the images,
                       include directory, name and extension.
        logo (str): The path of the logo with directory,
                        name and extension.
        builders(dict): Dictionary with the classes of possibles builders
    """

    def __init__(self, path: str,
                 print_paper_size: str, images: list, logo: str) -> None:
        new_form_path = os.path.join(os.path.dirname(__file__),
                                     "template_db_new.json")
        old_form_path = os.path.join(os.path.dirname(__file__),
                                     "template_db.json")
        '''Structure of the json files in 'new_form_path' and 'old_form_path' is:

        A list of dictionaries each represent a field in the form,
        the keys are:
            "label": the name of the field
            "value": a string to put in front of label
            "position": a dictionary with the coordinates of the label in the
                        .pdf file, depending on the paper size (key)
            "varname": the name of the variable in blender
        '''
        self.form_paths = {"OLD": old_form_path,
                           "NEW": new_form_path}
        self.path = path
        self.print_paper_size = print_paper_size
        self.images = images
        self.logo = logo
        self.builders = {"OLD": Old_Template_Builder,
                         "NEW": New_Template_Builder}

    def add_centered_text(self, builder, text):
        # Define a style for the centered text
        styles = getSampleStyleSheet()
        centered_style = styles["Title"]
        centered_style.alignment = TA_CENTER

        # Add centered text at the top of the page
        builder.c.setFont(centered_style.fontName, centered_style.fontSize)
        builder.c.drawCentredString(builder.pagesize[0] / 2, builder.pagesize[1] - 36, text)

    def make(self, template: str, query_result) -> None:
        """Make the .pdf file with the style indicated in 'template'."""
        builder = self.builders[template](self.path, self.print_paper_size)
        form_path = self.form_paths[template]
        form_info = open_json_file(form_path)
        form = PDF_Form_Content(form_info)

        for i, image in enumerate(self.images):
            if not image:
                continue

            builder.draw_main_image(image)
            builder.draw_logo(self.logo)

            if query_result.get(i):
                form_info = fill_form(form, query_result[i])
                builder.draw_info(form_info)

            builder.draw_block_info()

            # Add centered text at the top of the page
            is_box_build = False
            for obj in bpy.data.objects:
                if obj.get("IS_BP_ASSEMBLY") and sn_utils.get_cabinet_bp(obj):
                    is_box_build = True
                    break
                
            if is_box_build:
                self.add_centered_text(builder, "Box Build")

            builder.show_page()
        builder.c.save()


def open_json_file(file: str) -> dict:
    """Open a json file and return a dictionary."""
    with open(file) as f:
        json_file = json.load(f)
    return json_file
