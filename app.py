import exiftool, shutil, logging, sys
from pathlib import Path
from os import getenv
from time import perf_counter

logging.basicConfig(stream=sys.stdout, format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

media_extensions = ('.jpg', '.jpeg', '.heic', '.heif', '.png', '.gif', '.dng', '.raf', '.cr2', '.cr3', '.nef', '.nrw', '.orf', '.arw', '.tif', '.tiff', '.mov', '.mp4', '.avi')
media_list = []
model_list = []

# ENV variables
input_folder = getenv('INPUT_FOLDER', 'input/')
output_folder = getenv('OUTPUT_FOLDER', 'output/')
run_mode = getenv('DRY_RUN', "True").lower()

start_time = perf_counter()

# Get image and video lists
try:
    input_media = [p for p in Path(input_folder).rglob("*") if p.suffix.lower() in media_extensions]
except PermissionError:
    logger.error("Check input folder permissions")
    sys.exit(1)

media_count = len(input_media)

if run_mode == "false":
    logger.info(f"Dry-Run is set to {run_mode}")
    logger.info(f"Media files to be processed: {media_count}")
else:
    logger.info(f"Dry-Run is set to {run_mode}. No files will be moved!")
    logger.info(f"Media files that would be processed: {media_count}")

try:
    with exiftool.ExifToolHelper() as et:
        media_metadata = et.get_metadata(input_media)

        for media in media_metadata:
            media_type = media.get('File:MIMEType', 'NoType')
            source_file = media.get('SourceFile')
            
            # For full extracted metadata output
            # print(f'{media}\n\n')

            # Model tag identification
            if "EXIF:Model" in media:
                media_model = media.get('EXIF:Model')

            elif "QuickTime:Model" in media:
                media_model = media.get('QuickTime:Model')

            else:
                media_model = "NoModel"

            model = "".join(char for char in (media_model) if char.isalnum())

            if model not in model_list:
                model_list.append(model)

            # Media tag identification
            if "video" in media_type:
                created = media.get('QuickTime:CreateDate', 'NoDate').split(' ')[0].replace(':', '-')
                media_list.append({"source": source_file, "description": "NoDescription", "model": model, "created": created})
                
            elif "image" in media_type:
                description = media.get('EXIF:ImageDescription', 'NoDescription')
                created = media.get('EXIF:DateTimeOriginal', 'NoDate').split(' ')[0].replace(':', '-')
                media_list.append({"source": source_file, "description": description, "model": model, "created": created})

            else:
                logger.warning(f"Unknown media type... Skipping file: {source_file}")

except ValueError:
    logger.warning(f"There were no files to process. If files were expected, ensure that input path is correct. It's currently set to: {input_folder}")

# Move the media files
for item in media_list:
    source_file = Path(item.get('source'))

    if "NoModel" not in item.get("model"):
        destination_dir = Path(output_folder + item.get('model') + "/" + item.get('created'))

    elif "Screenshot" in item.get("description"):
        destination_dir = Path(output_folder + "screenshots/" + item.get('created'))

    else:
        destination_dir = Path(output_folder + "unknown/" + item.get('created'))

    target_file_path = destination_dir / source_file.name

    if run_mode == "false":
        try:
            move_start_time = perf_counter()

            logger.info(f"Moving: {source_file}")
            destination_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(src=str(source_file), dst=str(target_file_path))

            move_end_time = perf_counter()

            move_execution_time = move_end_time - move_start_time

            logger.info(f"Successfully moved {source_file} > {target_file_path} in {move_execution_time:.6f} seconds")
        except PermissionError:
            logger.error("Check output folder permissions")
            sys.exit(1)

    else:
        logger.info(f"Would have moved - {source_file} > {target_file_path}")

end_time = perf_counter()

execution_time = end_time - start_time

if run_mode == "false":
    logger.info(f"Completed processing of {media_count} files in {execution_time:.2f} seconds")
    logger.info(f"The average speed was {media_count/execution_time:.2f} files/sec")
    sys.exit(0)
else:
    logger.info(f"Completed dry run of {media_count} files in {execution_time:.2f} seconds")
    sys.exit(0)
