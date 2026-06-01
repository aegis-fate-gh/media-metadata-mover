# media-metadata-mover

[Source Code](https://github.com/aegis-fate-gh/media-metadata-mover) on Github

## Description
This image contains python code that when given media files, attempts to run them through the embedded [ExifTool](https://exiftool.org). it also makes use of the the [PyExifTool](https://pypi.org/project/PyExifTool/) library. It then looks for exif tags containing creation dates, descriptions, and camera models.

From there, when 'False' is set via the DRY_RUN environment variable, it moves the files accordingly. 

## Process Flow
Here's an example process flow on a single image:

1. Script detects an image named 2026-05-04 19.25.17.heic and runs it through exiftool
2. Exiftool gets the creation date and camera model name. The script then formats them as 2026-05-04 and iPhone16Pro respectively
3. Using the camera model and creation date, it then create folders as needed
4. The script then moves the file from input/2026-05-04 19.25.17.heic to output/iPhone16Pro/2026-05-04/2026-05-04 19.25.17.heic

### Caveats
1. If both the date, and camera model are unknown, you can end up with scenarios where files are moved to folders like: output/unknown/0000-00-00/Insert_File_Here
2. Images without a model name that are tagged with "Screenshot" in their description will instead be moved to folders like this: output/screenshots/DATE/Insert_File_Here

## Valid media formats
This script is set up to only look for the specific media formats noted below:

**Images:**
- .arw
- .cr2 / .cr3
- .dng
- .gif
- .heic / .heif
- .jpg / .jpeg
- .nef
- .nrw
- .orf
- .png
- .raf
- .tif / .tiff

**Video:**
- .avi
- .mov
- .mp4

Many more formats are supported via ExifTool, but these are the types typically associated with modern cameras.

## Environment Variables
This image takes 3 environment variables:

| Variable | Default | Type | Valid Inputs
| ----------- | ----------- | ----------- | ----------- |
| INPUT_FOLDER | input/ | Path | Any valid path |
| OUTPUT_FOLDER | output/ | Path | Any valid path |
| DRY_RUN | True | String | True/False |

- INPUT_FOLDER: The path that the script will look in for media files
- OUTPUT_FOLDER: The path the script will move the files to
- DRY_RUN: By default, the script runs in dry-run mode. To actually have the script move the files, this variable must be set to False.

## Example compose file
This example mounts a volume named media in /media within the container. It then sets the input and output environment variables to 2 folders within that media volume. Dry_RUN is commented out to allow verification that the script will work as intended prior to a live run.
```
---
version: '3.8'

services:
  media-metadata-mover:
    image: aegisfatedh/media-metadata-mover:latest
    container_name: media-metadata-mover
    volumes:
      - '/media:/media'
    environment:
      - PUID=1000
      - PGID=1000
      # Only uncomment when you're ready for the script to actually move the files
      # - DRY_RUN=False
      - INPUT_FOLDER=/media/input/
      - OUTPUT_FOLDER=/media/output/
```