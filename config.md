# Anki2Images Add-On Configuration Guide

## Configuration File: `config.json`

The `config.json` file is used to configure various settings for the Anki2Images add-on. Below is a description of each setting and how to modify them.

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

### config.json settings
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
please refer to jinja documentation
https://jinja.palletsprojects.com/en/3.1.x/
### autocrop 
ImageMagick is needed: https://imagemagick.org/