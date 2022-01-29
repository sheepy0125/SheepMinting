"""
Sheepy NFT Image Creator
Used for piecing together images
"""

# Imports
import logging
import numpy as np
import sys
from random import randint, choice
from pathlib import Path
from shutil import rmtree, make_archive
from jsonc_parser.parser import JsoncParser
from jsonc_parser.errors import FileError, ParserError
from PIL import Image, ImageColor
from tqdm import tqdm
from json import dump, load
from time import time, strftime, gmtime
from os import devnull

# Constants
ROOT_PATH = Path(__file__).parent.parent  # Will be in `minting`
PIECE_TOGETHER_PATH = Path(__file__).parent  # Will be in `piece_together`
IMAGES_PATH = ROOT_PATH / "sheep_images"
# Config
DEBUG = False
CONFIG_NAME = "config.jsonc"
CONFIG_PATH = PIECE_TOGETHER_PATH / CONFIG_NAME
OUTPUT_PATH: Path
MAX_NUMBER_NFTS: int
SHOULD_ZIP_OUTPUT: bool
SHOULD_JSON_OUTPUT: bool
COLORS: dict
scope = "GENERAL"
nfts_done: int

# Logger

# Add logger context filter
class ContextFilter(logging.Filter):
    """Filter for adding scope to log messages"""

    def filter(self, record):
        global scope
        record.scope = scope
        return True


logger = logging.getLogger(__name__)  # Regular logger
Image.init()  # PIL logger

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(scope)s:%(message)s",
    level=logging.DEBUG if DEBUG else logging.INFO,
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
# We have two loggers, the PIL logger and the regular logger
for name in logging.Logger.manager.loggerDict:
    logger_to_add = logging.getLogger(name)
    logger_to_add.addFilter(ContextFilter())
    # Disable debug for PIL logger
    if name == "PIL":
        logger_to_add.setLevel(logging.INFO)
logger.debug("Logger initialized")


# Functions
def cannot_continue():
    """Prints an error message and exits the program"""

    logger.error(f"Cannot continue! Exiting...")
    exit(1)


# Stolen from
# https://stackoverflow.com/questions/3752476/python-pil-replace-a-single-rgba-color
def global_fill(image: Image, original_color: str, replace_color: str):
    """Globally replace one color with another for an image"""

    # Convert hex colors into RGB values
    original_color = ImageColor.getcolor(f"#{original_color}", "RGB")
    replace_color = ImageColor.getcolor(f"#{replace_color}", "RGB")

    # Find pixels of colors to replace
    image_data = np.array(image)
    red, green, blue, _ = image_data.T
    first_color_areas = (
        (red == original_color[0])
        & (green == original_color[1])
        & (blue == original_color[2])
    )
    # Replace colors
    image_data[..., :-1][first_color_areas.T] = replace_color

    return Image.fromarray(image_data)


# Parse configuration
scope = "CONFIG_PARSE"
if not CONFIG_PATH.is_file():
    logger.error(f"Cannot find config file: {CONFIG_PATH}")
    cannot_continue()

with open(CONFIG_PATH) as config_file:
    try:
        try:
            config = JsoncParser.parse_str(config_file.read())
        except (FileError, ParserError) as e:
            logger.error(f"Invalid JSONC file:{CONFIG_NAME}:\n{e}")
            cannot_continue()

        # Read from config
        try:
            OUTPUT_PATH = Path(config["outputDirectory"])
            MAX_NUMBER_NFTS = int(config["numberNftsToMint"])
            SHOULD_JSON_OUTPUT = config["shouldJsonOutput"]
            SHOULD_ZIP_OUTPUT = config["shouldZipOutput"]
            COLORS = config["colors"]
        except (KeyError, TypeError):
            logger.error("Config file is missing required keys!")
            cannot_continue()

        # Validate config
        if OUTPUT_PATH.is_file():
            logger.error(f"Output directory, {OUTPUT_PATH}, is a FILE!")
            cannot_continue()
        if not OUTPUT_PATH.exists():
            logger.debug("Creating output directory...")

        # Detect if there are any images in the output folder
        if OUTPUT_PATH.exists() and OUTPUT_PATH.is_dir():
            if next(OUTPUT_PATH.glob("*"), None) is not None:
                logger.warning(
                    f"Output folder is not empty! This will overwrite existing files!"
                )
                if input('Press enter to continue, or type "exit" to exit...') != "":
                    cannot_continue()
            rmtree(str(OUTPUT_PATH))
            logger.debug("Output folder is empty")

        try:
            OUTPUT_PATH.mkdir(parents=True)
            Path(OUTPUT_PATH / "upload").mkdir(parents=False)
            Path(OUTPUT_PATH / "private").mkdir(parents=False)
        except OSError as e:
            logger.error(
                f"Could not create output directory: {OUTPUT_PATH}."
                f"Is there a permission error?\n{e}"
            )
            cannot_continue()
        else:
            logger.debug("Output directory exists")
        if any(
            (
                color_section not in COLORS
                or any((not isinstance(color, str)) for color in COLORS[color_section])
            )
            for color_section in ("head_area", "wool", "background")
        ):
            logger.error(
                "Colors are invalid! They must be a list of hex values (without #) "
                "for head_area, wool, and background"
            )
            cannot_continue()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        cannot_continue()

    logger.info("Parsed config file")

    # ConfirmCOLORS[
    logger.info(f"{OUTPUT_PATH=}")
    logger.info(f"{MAX_NUMBER_NFTS=}")
    logger.info(f"{SHOULD_JSON_OUTPUT=}")
    logger.info(f"{COLORS=}")
    if input('Press enter to continue, or type "exit" to exit...') != "":
        cannot_continue()

# Gather images
scope = "GATHER_IMAGES"
logger.info("Gathering images...")
image_sections = {
    "head_face": {
        "path": ROOT_PATH / IMAGES_PATH / "head" / "face",
        "size": (32, 32),
        "colors_key": {
            "face_color": "FFFFFF",
        },
    },
    "head_top": {
        "path": ROOT_PATH / IMAGES_PATH / "head" / "top",
        "size": (42, 32),
        "colors_key": {
            "primary_wool": "111001",
        },
    },
    "body": {
        "path": ROOT_PATH / IMAGES_PATH / "body",
        "size": (128, 64),
        "colors_key": {
            "primary_wool": "111001",  # Body wool
            "secondary_wool": "111002",  # Tail wool, OPTIONAL
        },
    },
}
total_number_images = 0
for image_section_name, image_section_info in image_sections.items():
    logger.debug(f"Gathering images from {image_section_name}")
    image_section_info["images"] = list(image_section_info["path"].glob("*.png"))
    total_number_images += len(image_section_info["images"])
    if not image_section_info["images"]:
        logger.error(f"No images found in {image_section_info['path']}")
        cannot_continue()
    image_section_info["images"] = sorted(image_section_info["images"])  # Numerical

# Give statistics about the images
logger.info("Gathered images")
logger.info(f"There are a total of {total_number_images} images")
for image_section, (image_section_name, image_section_info) in enumerate(
    image_sections.items()
):
    logger.info(
        f"The section, {image_section:02d}-{image_section_name}, has a total of "
        f'{len(image_section_info["images"])} images',
    )

# Combine images together into a single image
# The image will be 164x96 pixels in size
# See `image_sections` for the image section sizes
scope = "COMBINE_IMAGES"

logger.info("Ready to start! Awaiting user input...")
if input('Press enter to continue, or type "exit" to exit...') != "":
    cannot_continue()

logger.info("Combining images together...")

done_configurations = [
    # Documentation purposes
    {
        "head_face": 2,
        "head_top": 1,
        "body": 0,
        # Will be indexes
        "colors": {
            "head_area": 3,
            "primary_wool": 2,
            "secondary_wool": 5,
        },
    }
]
done_configurations.clear()

start_time = time()
for nfts_done in tqdm(range(MAX_NUMBER_NFTS)):
    # Randomize an image configuration
    image_configuration = {}
    for image_section in image_sections:
        image_configuration[image_section] = randint(
            0, len(image_sections[image_section]["images"]) - 1
        )
    image_configuration["colors"] = {
        "face": randint(0, len(COLORS["head_area"]) - 1),
        "primary_wool": randint(0, len(COLORS["wool"]) - 1),
        "secondary_wool": randint(0, len(COLORS["wool"]) - 1),
        "background": randint(0, len(COLORS["background"]) - 1),
    }
    # Has this image configuration already been done?
    if image_configuration in done_configurations:
        continue  # Do it again!
    done_configurations.append(image_configuration)

    # Create a new image
    image = Image.new(mode="RGBA", size=(164, 96), color=(255, 255, 255))

    # Add the body
    with Image.open(
        image_sections["body"]["images"][image_configuration["body"]]
    ) as body:
        # Body wool color
        body = global_fill(
            body,
            image_sections["body"]["colors_key"]["primary_wool"],
            COLORS["wool"][image_configuration["colors"]["primary_wool"]],
        )
        # Tail wool color
        body = global_fill(
            body,
            image_sections["body"]["colors_key"]["secondary_wool"],
            COLORS["wool"][image_configuration["colors"]["secondary_wool"]],
        )
        # Paste
        image.paste(body, (21, 32))

    # Add the head top
    with Image.open(
        image_sections["head_top"]["images"][image_configuration["head_top"]]
    ) as head_top:
        # Head top wool color
        head_top = global_fill(
            head_top,
            image_sections["head_top"]["colors_key"]["primary_wool"],
            COLORS["wool"][image_configuration["colors"]["primary_wool"]],
        )
        # Paste
        image.paste(head_top, (0, 0))

    # Add the head face
    with Image.open(
        image_sections["head_face"]["images"][image_configuration["head_face"]]
    ) as head_face:
        # Head face color
        head_face = global_fill(
            head_face,
            image_sections["head_face"]["colors_key"]["face_color"],
            COLORS["head_area"][image_configuration["colors"]["face"]],
        )
        # Paste
        image.paste(head_face, (5, 24), mask=head_face)  # Mask here uses alpha channel

    # Background color
    image = global_fill(
        image,
        "FFFFFF",
        COLORS["background"][image_configuration["colors"]["background"]],
    )

    # Save the image
    image.save(
        OUTPUT_PATH / "upload" / f"IMG {nfts_done}.png",
        format="PNG",
        optimize=True,
        compress_level=9,
    )

    # Create JSON data
    if not SHOULD_JSON_OUTPUT:
        continue

    with open(
        OUTPUT_PATH / "private" / f"JSON_IMG_DATA {nfts_done}.json", "w"
    ) as json_file:
        dump(image_configuration, json_file)

    with open(
        OUTPUT_PATH / "upload" / f"JSON_NFT_DATA {nfts_done}.json", "w"
    ) as json_file:
        cost = randint(1, 100) / 10000
        # Rarity will be on a scale of 0-10 and will factor in the total number of NFTs and the NFT cost
        rarity = ((nfts_done / MAX_NUMBER_NFTS) * 10 + (cost / 0.01) * 10) / 2
        dump(
            {
                "name": f"sheep-nft-{nfts_done}",
                "description": f"An image of sheep number {nfts_done}",
                # For more info on `image`, see
                # https://docs.pinata.cloud/nfts#how-to-associate-metadata-with-your-nft
                "image": "ipfs://YOUR_METADATA_CID",
                "attributes": {
                    "id": nfts_done,
                    "cost": cost,
                    "rarity": rarity,
                },
            },
            json_file,
        )

# Zip the output folder
scope = "ZIP_OUTPUT"
if SHOULD_ZIP_OUTPUT:
    logger.info("Zipping output...")
    try:
        make_archive(OUTPUT_PATH, "zip", OUTPUT_PATH)
    except Exception as e:
        logger.error(f"Failed to zip output: {e}")
        logger.error("Continuing without zipping...")

end_time = time()
scope = "GENERAL"
logger.info("Done!")

# Done! Print some statistics
scope = "GATHER_STATISTICS"

logger.info("Would you like to gather some statistics?")
if input('Press enter to continue, or type "exit" to exit...') != "":
    cannot_continue()
logger.info("Gathering statistics, this may take a while...")

statistics_to_log = []

# Number of NFTs
statistics_to_log.append(f"There were {MAX_NUMBER_NFTS} unique NFTs created")

# Time taken
statistics_to_log.append(
    f'It took {strftime("%H:%M:%S", gmtime(end_time - start_time))} to create the NFTs'
)

# Rarest NFTs
if SHOULD_JSON_OUTPUT:
    with tqdm(
        # The progress bar shouldn't show when not in debug mode
        total=MAX_NUMBER_NFTS,
        file=open(devnull, "w") if not DEBUG else sys.stdout,
    ) as progress_bar:
        logger.debug("Gathering rarest NFTs...")
        statistics_to_log.append("The top-ten rarest NFTs are:")
        nft_rarities = {}
        for nfts_done in range(MAX_NUMBER_NFTS):
            progress_bar.update(1)
            with open(
                OUTPUT_PATH / "upload" / f"JSON_NFT_DATA {nfts_done}.json", "r"
            ) as json_file:
                nft_data = load(json_file)
            nft_rarities[nft_data["attributes"]["rarity"]] = {
                "id": nft_data["attributes"]["id"],
                "cost": nft_data["attributes"]["cost"],
            }

        nft_rarities_list = list(nft_rarities)
        nft_rarities_list.sort(reverse=True)

        for nft_rarity in nft_rarities_list[:10]:
            nft_data = nft_rarities[nft_rarity]
            statistics_to_log.append(
                f'{nft_data["id"]}: {nft_rarity} ({nft_data["cost"]})'
            )

for to_log in statistics_to_log:
    logger.info(to_log)

scope = "GENERAL"
logger.info("Ready to exit...")
input()
