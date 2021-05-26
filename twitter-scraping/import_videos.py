import json

from db import *

def main():
    db_file = "./db.db"
    create_videos_table()

    # Read JSON file
    data = None
    filename = './data/videos.json'
    with open(filename) as f:
        data = json.load(f)

    # TODO: Remove
    for category in data.keys():
        for channel in data[category].keys():
            for video in data[category][channel]:
                video_tpl = (
                                category,
                                channel,
                                video[0],
                                video[1],
                                int(video[2]),
                                video[3]
                            )
                vid_id = create_video(video_tpl)
                print(vid_id)

if __name__ == '__main__':
    main()