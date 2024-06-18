# anki-export-as-picture
Export Anki cards as picture with flexible jinja2 templates ans CSS styling
You can use anki styling from anki card template CSS section.
Anki templates can be easily transformed to jinja2 templates with ChatGPT.

# Anki2Images Add-On Configuration Guide

## Configuration File: `meta.json` 

Addon is configurable through anki-menue: Tools-->add-ons
Please select addon and then click on "config".
Settings are stored in meta.json.
config.json is storing default values 

### Example Configuration


```json
{
    "debug": false
    "resolution": [1920, 1080],
    "last_output_folder": "",
    "replace_cloze": false,
    "exclude_fields": [
      "Field-Containing-Sound-Tags-Only",
      "Question Mask"
    ],
    "default_template": "template.html",
    "default_css": "styles.css",
    "auto_crop": false,
    "note_card_templates": [
        {
            "note_type": "MultipleChoice",
            "card_type": "Question",
            "template": "template_multiple_choice.html",
            "css": "styles_multiple_choice.css"
        }
    ]
}
```

### settings
1. debug
Type: boolean
Description: Enables or disables debug mode. When enabled, temporary html file will not be deleted and additional debug information will be logged. 
Default: false
Example: "debug": true
2. resolution
Type: array
Description: Specifies the resolution of the generated images. The resolution is defined as [width, height].
Default: [1920, 1080]
Example: "resolution": [3000, 2000]
3. last_output_folder
Type: string
Description: Stores the path of the last output folder selected by the user. This path is used to pre-select the output folder in subsequent runs.
Default: ""
Example: "last_output_folder": "C:/Users/your_username/Documents/AnkiImages"
4. replace_cloze
Type: boolean
Description: Enables or disables the replacement of cloze deletions with <cloze> tags.
Default: false
Example: "replace_cloze": true
5. exclude_fields
Type: array
Description: Specifies a list of field names to exclude from processing. Exlude e.g. Question Mask from Image Occlusion template or fields with sound tags.
Default: []
Example: "exclude_fields": ["Field1", "Field2"]
6. default_template
Type: string
Description: Specifies the filename of the default HTML template to use for generating images.
Default: "template.html"
Example: "default_template": "my_custom_template.html"
7. default_css
Type: string
Description: Specifies the filename of the default CSS file to use for styling the generated images.
Default: "styles.css"
Example: "default_css": "custom_styles.css"
8. auto_crop
Type: boolean
Description: Enables or disables auto-cropping of generated images.
Default: false
Example: "auto_crop": true
9. note_card_templates
Type: array
Description: A list of tuples that define specific templates and CSS files for specific note types and card types. Each tuple consists of:
   - note_type: The note type name.
   - card_type: The card type name.
   - template: The filename of the HTML template to use for this note type and card type.
   - css: The filename of the CSS file to use for this note type and card type.

### html templates
The add-on uses jinja in template files
please refer to jinja documentation
https://jinja.palletsprojects.com/en/3.1.x/


#### Default Template (template.html)
This template defines the HTML structure used to render Anki cards as images. Below is an explanation of the key elements:
```html
<!doctype html>
<html>
<head>
    <style>
        <!-- Inject the CSS content from the configured CSS file -->
        {{ css }}
    </style>
</head>
<body>
<!-- Check if the note type is not one of the Image Occlusion types -->
{% if note_type not in ['Image Occlusion', 'Image Occlusion Enhanced', 'Image Occlusion Enhanced+'] %}
    <table class="custom-table-left">
        <!-- Loop through each field in the fields dictionary -->
        {% for field, value in fields.items() %}
            <!-- Only display non-empty fields -->
            {% if value != "" %}
            <tr>
                <!-- Convert the field name to lowercase for CSS class and display its value -->
                <td><div class="{{ field|lower }}">{{ value }}</div></td>
            </tr>
            {% endif %}
        {% endfor %}
    </table>
{% endif %}

</body>
</html>
```
- {{ css }}: This will be replaced by the content of the CSS file.
- The body tag styles ensure that the content is centered on the page.
- The template uses Jinja2 syntax to conditionally render fields based on the note type.
- For non-Image Occlusion notes, it creates a table with each field as a row.
- For Image Occlusion notes, it creates a table with specific fields (Header and Image).

### autocrop 
for autocrop, you need to download and install ImageMagick commandline tool.
Windows: In system path, you need to add the path to the 