import sys
from pathlib import Path
import json
import shutil

import piexif
from PIL import Image
from datetime import datetime


def assign(input_dir: Path, output_dir: Path):

    album = input_dir / "your_facebook_activity" / "posts" / "album"

    for json_file in album.glob("*.json"):
        print(json_file)
        with open(json_file, "r") as f:
            data = json.load(f)
        for e in data["photos"]:
            uri = e["uri"]
            if not uri.endswith(".jpg"):
                continue
            taken_timestamp = (
                e.get("media_metadata", {})
                .get("photo_metadata", {})
                .get("exif_data", [{}])[0]
                .get("taken_timestamp", None)
            )
            creation_timestamp = e.get("creation_timestamp", None)

            if taken_timestamp:
                epoch = taken_timestamp
            elif creation_timestamp:
                epoch = creation_timestamp
            else:
                assert False
            exif_date = datetime.utcfromtimestamp(epoch).strftime("%Y:%m:%d %H:%M:%S")

            # print(uri, taken_timestamp, creation_timestamp)

            output_path = output_dir / Path("/".join(Path(uri).parts[-2:]))

            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(input_dir / uri, output_path)

            exif_dict = {
                "0th": {},
                "Exif": {piexif.ExifIFD.DateTimeOriginal: exif_date},
            }
            print(f"{output_path} @ {exif_date}")
            piexif.insert(piexif.dump(exif_dict), str(output_path))


if __name__ == "__main__":
    assign(Path(sys.argv[1]), Path("out"))
