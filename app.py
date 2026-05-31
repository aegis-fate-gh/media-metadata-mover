import exiftool, shutil
from pathlib import Path
from os import getenv
from time import perf_counter

media_extensions = ('.jpg', '.jpeg', '.heic', '.png', '.gif', '.mov', '.mp4', '.avi')
media_list = []
model_list = []

# ENV variables
input_folder = getenv('INPUT_FOLDER', 'input/')
output_folder = getenv('OUTPUT_FOLDER', 'output/')
run_mode = getenv('MODE', 'dry-run')

start_time = perf_counter()
print(f"Mode set to: {run_mode}")

# Get image and video lists
input_media = [p for p in Path(input_folder).iterdir() if p.suffix.lower() in media_extensions]

media_count = len(input_media)

print(f"Media files to be processed - {media_count}\n")

try:
    with exiftool.ExifToolHelper() as et:
        media_metadata = et.get_metadata(input_media)

        for media in media_metadata:
            media_type = media.get('File:MIMEType', 'NoType')
            source_file = media.get('SourceFile')

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
                print("Unknown media type... Skipping file")

except ValueError:
    print("There were no files to process. Nothing to see here....")

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

    if run_mode.lower() == "live":
        print(f"Moving: {source_file}")
        destination_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(src=str(source_file), dst=str(target_file_path))
        print(f"Successfully moved to: {target_file_path}")

    else:
        print(f"Input file path: {source_file}")
        print(f"Destination file path: {target_file_path}\n")

end_time = perf_counter()

execution_time = end_time - start_time

print(f"Completed processing of {media_count} files in {execution_time:.2f} seconds")
print(f"The average speed was {media_count/execution_time:.2f} files/sec")
