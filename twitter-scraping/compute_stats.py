from db import *

def main():
	while True:
		video_id = next_uncomputed_video()
		if not video_id:
			break

		print("Processing stats for video ID " + str(video_id) + "...")
		compute_stats(video_id)


if __name__ == "__main__":
	main()