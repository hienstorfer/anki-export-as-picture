import os
import re
import logging
import sys
import subprocess
from aqt import mw
from aqt.utils import showInfo
from aqt.qt import QAction, QFileDialog
from aqt.browser import Browser
from aqt import gui_hooks
from jinja2 import Template
from bs4 import BeautifulSoup

# Get the add-on directory dynamically
addon_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(addon_dir, 'lib'))

# Now we can import the Html2Image module
from html2image import Html2Image

# Load configuration from meta.json
def load_meta_config():
    try:
        config = mw.addonManager.getConfig(__name__)
        return config
    except Exception as e:
        showInfo(f"Failed to load configuration from meta.json: {e}")
        return {}

def save_meta_config(config):
    try:
        mw.addonManager.writeConfig(__name__, config)
    except Exception as e:
        showInfo(f"Failed to save configuration to meta.json: {e}")

config = load_meta_config()

# Ensure the logging directory exists
log_dir = os.path.join(addon_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'error_log.txt')
logging_level = logging.DEBUG if config.get("debug", False) else logging.INFO

# Set up a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)

# Create file handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging_level)

# Create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Function to display error message on the screen
def show_error_message(message):
    showInfo(message)
    logger.error(message)

def replace_cloze_deletions(text):
    return re.sub(r'{{c\d+::(.*?)}}', r'<cloze>\1</cloze>', text)

def log_debug_message(message):
    try:
        logger.debug(message)
    except Exception as e:
        show_error_message(f"Failed to log message: {e}")

def load_css(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            log_debug_message(f"Loaded CSS content from {file_path}")
            return css_content
    except Exception as e:
        log_debug_message(f"Error loading CSS file: {e}")
        raise

def load_html_template(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            template_content = Template(f.read())
            log_debug_message(f"Loaded HTML template from {file_path}")
            return template_content
    except Exception as e:
        log_debug_message(f"Error loading HTML template file: {e}")
        raise

def add_media_path_to_images(html, media_folder):
    media_folder = media_folder.replace("\\", "/")
    def replace_src(match):
        src = match.group(1)
        if not src.startswith(media_folder):
            return f'src="{media_folder}/{src}"'
        return match.group(0)
    return re.sub(r'src="([^"]+)"', replace_src, html)

def strip_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def get_template_and_css(note_type, card_type):
    for entry in config.get("note_card_templates", []):
        if entry["note_type"] == note_type and entry["card_type"] == card_type:
            return entry["template"], entry["css"]
    return config.get("default_template", "template.html"), config.get("default_css", "styles.css")

def generate_html_content(card_id, template_filename, css, note_type, card_type, media_folder, note_fields):
    try:
        template = load_html_template(os.path.join(addon_dir, template_filename))
        resolution = tuple(config.get("resolution", [1920, 1080]))  # Use resolution from config

        log_debug_message(f"Using template: {template_filename}")
        log_debug_message(f"Using resolution: {resolution}")

        # Apply cloze replacement if enabled
        if config.get("replace_cloze", False):
            note_fields = {k: replace_cloze_deletions(v) for k, v in note_fields.items()}

        html_content = template.render(
            css=css,
            fields=note_fields,
            note_type=note_type,
            card_type=card_type
        )
        html_content = add_media_path_to_images(html_content, media_folder)
        log_debug_message(f"Generated HTML content for card {card_id}")
        return html_content, resolution
    except Exception as e:
        log_debug_message(f"Error generating HTML content for card {card_id}: {e}")
        raise

def auto_crop_image(image_path):
    try:
        subprocess.run(['magick', 'convert', image_path, '-trim', image_path], check=True)
        log_debug_message(f"Auto-cropped image: {image_path}")
    except subprocess.CalledProcessError as e:
        log_debug_message(f"Error auto-cropping image: {e}")

def is_cloze_note_type(note):
    for field_name, field_value in note.items():
        if re.search(r'{{c\d+::.*?}}', field_value):
            return True
    return False

def export_notes_as_images(browser: Browser):
    log_debug_message("Starting export process...")
    log_debug_message(f"Configuration: {config}")

    output_folder = QFileDialog.getExistingDirectory(caption="Select Output Folder", directory=config.get("last_output_folder", ""))
    if not output_folder:
        log_debug_message("No output folder selected.")
        return

    # Save the selected output folder to config
    config["last_output_folder"] = output_folder
    save_meta_config(config)

    try:
        hti = Html2Image(output_path=output_folder)

        card_ids = browser.selected_cards()
        if not card_ids:
            showInfo("No cards selected.")
            return

        media_folder = mw.col.media.dir()  # Get the standard media folder path
        log_debug_message(f"Media folder: {media_folder}")

        exclude_fields = config.get("exclude_fields", [])
        processed_notes = set()

        for card_id in card_ids:
            card = mw.col.get_card(card_id)
            note = card.note()
            note_id = note.id

            if note_id in processed_notes:
                continue

            note_type = note.note_type()['name']
            card_template = card.template()  # Get the card template
            card_type = card_template['name']  # Get the card type name
            card_number = card_template['ord']  # Get the card number

            # Determine card_id based on presence of 'CardID' field and its content
            card_id_text = ''
            try:
                card_id_text = strip_html(note['CardID']).strip()
            except KeyError:
                log_debug_message(f"CardID field missing for note {note.id}")

            if not card_id_text:
                card_id_text = str(note.id)
                log_debug_message(f"Using note ID {note.id} as card ID")

            note_fields = {field: add_media_path_to_images(note[field], media_folder) for field in note.keys() if field not in exclude_fields}

            template_filename, css_filename = get_template_and_css(note_type, card_type)
            css_file_path = os.path.join(addon_dir, css_filename)
            try:
                css_content = load_css(css_file_path)
                if is_cloze_note_type(note):
                    html_content, resolution = generate_html_content(card_id_text, template_filename, css_content, note_type, card_type, media_folder, note_fields)
                    log_debug_message(f"Generated HTML content for card {card_id_text}")

                    temp_html_file = os.path.join(output_folder, f'temp_{card_id_text}_card_{card_number}.html')
                    with open(temp_html_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    log_debug_message(f"Temporary HTML file created: {temp_html_file}")

                    output_image = f'{card_id_text}_card{card_number}.png'
                    log_debug_message(f"Attempting to create image for card {card_id_text} as {output_image}")

                    hti.screenshot(html_file=temp_html_file, save_as=output_image, size=resolution)

                    if os.path.exists(os.path.join(output_folder, output_image)):
                        log_debug_message(f"Image successfully created: {output_image}")
                        if config.get("auto_crop", False):
                            auto_crop_image(os.path.join(output_folder, output_image))
                    else:
                        log_debug_message(f"Image creation failed for card {card_id_text}")

                    if not config.get("debug", False):
                        os.remove(temp_html_file)
                        log_debug_message(f"Temporary HTML file removed: {temp_html_file}")

                    # Skip processing other cards of this note
                    processed_notes.add(note_id)
                    continue

                html_content, resolution = generate_html_content(card_id_text, template_filename, css_content, note_type, card_type, media_folder, note_fields)
                log_debug_message(f"Generated HTML content for card {card_id_text}")

                temp_html_file = os.path.join(output_folder, f'temp_{card_id_text}_card_{card_number}.html')
                with open(temp_html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                log_debug_message(f"Temporary HTML file created: {temp_html_file}")

                output_image = f'{card_id_text}_card{card_number}.png'
                log_debug_message(f"Attempting to create image for card {card_id_text} as {output_image}")

                hti.screenshot(html_file=temp_html_file, save_as=output_image, size=resolution)

                if os.path.exists(os.path.join(output_folder, output_image)):
                    log_debug_message(f"Image successfully created: {output_image}")
                    if config.get("auto_crop", False):
                        auto_crop_image(os.path.join(output_folder, output_image))
                else:
                    log_debug_message(f"Image creation failed for card {card_id_text}")

                if not config.get("debug", False):
                    os.remove(temp_html_file)
                    log_debug_message(f"Temporary HTML file removed: {temp_html_file}")

            except Exception as e:
                log_debug_message(f"Error processing card ID {card_id_text}: {e}")
                continue

    except Exception as e:
        log_debug_message(f"Error in export_notes_as_images: {e}")

def add_browser_menu_entry(browser):
    action = QAction("Export Selected Notes as Images", browser)
    action.triggered.connect(lambda _, b=browser: export_notes_as_images(b))
    browser.form.menuEdit.addAction(action)

def init_addon():
    gui_hooks.browser_will_show.append(add_browser_menu_entry)

init_addon()
