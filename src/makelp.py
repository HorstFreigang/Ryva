#! /usr/bin/env python

import argparse, time, subprocess

audio_source = "" # audio source file
album_infos = "" # album and tracklist infos
count = 0 # counter
error = 0 # error

# album infos
artist = ""
album = ""
genre = ""
year = ""

# text colors
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
NC = "\033[0m"

# prefixes numbers lower then 10 with a '0'
def num_zero_prefix(cnt):
	if cnt < 10:
		cnt = "0" + str(cnt)
	else:
		cnt = cnt

	return cnt

# gets default album information
def get_album_info(infos):
	artist = infos
	album = infos
	year = infos
	genre = infos

# calculates duration of track
def calc_duration(start, end):
	if end != "":
		t1 = start.split(":")
		t2 = end.split(":")
		s1 = int(t1[0]) * 60 + int(t1[1])
		s2 = int(t2[0]) * 60 + int(t2[1])
		d = s2 - s1

		dura = str(d)

	else:
		dura = ""

	return dura

# creates audio files
def create_track(args):
	audio_source = args.audio_source.strip()
	album_infos = args.album_infos.strip()

	file = open(album_infos, "r")
	track_list = file.read()
	file.close()

	lines = track_list.split("\n")
	for idx, line in enumerate(lines):
		track_info = line.split(";")
		start_time = track_info[0]
		duration = calc_duration(track_info[0], track_info[1])
		filename = track_info[2]

		cmd = ["ffmpeg", "-nostdin", "-y", "-loglevel", "quiet"]

		cmd.append("-ss")
		cmd.append(str(start_time))
		cmd.append("-i")
		cmd.append(audio_source)

		if duration != "":
			cmd.append("-t")
			cmd.append(str(duration))

		cmd.append(str(num_zero_prefix(idx + 1)) + " - " + str(filename) + ".mp3")
		
		p_ffmpeg = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		while True:
			line = p_ffmpeg.stdout.readline()
			if not line:
				break
			print line
		p_ffmpeg.wait()

# main function
def main():
	parser = argparse.ArgumentParser(description="With makelp you can extract audio clips from an audio-source. That source can be a ripped audio-track from a YoutTube video. All track infos, like start-time, end-time and song name, need to be in a seperate text file. Look for a detailed help at https://github.com/horstfreigang/makelp.")

	required = parser.add_argument_group("Required arguments");
	required.add_argument("-i", "--input", help="Audio source file", dest="audio_source", metavar="", type=str, required=False)
	required.add_argument("-t", "--tracklist", help="Plain text file with album and track infos", dest="album_infos", metavar="", type=str, required=True)

	optional = parser.add_argument_group('Optional arguments');
	optional.add_argument("-c", "--cover", help="Image file for the album cover", dest="cover", metavar="", type=str, default="")
	optional.add_argument("-I", "--id3", metavar="", help="Write ID3v2 tags in output files")

	parser.set_defaults(func=create_track)
	args = parser.parse_args()
	args.func(args)

if __name__ == "__main__":
	main()