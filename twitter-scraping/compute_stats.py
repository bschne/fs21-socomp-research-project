from db import *

def main():
	while True:
		video_id = next_uncomputed_video()
		if not video_id:
			break

		compute_stats(video_id)


if __name__ == "__main__":
	main()