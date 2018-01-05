#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, argparse, subprocess

cue = []
album_infos = []
output_path = ''

# text colors

RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
NC = "\033[0m"


# TODO:
# youtube-dl integration
# fix ffmpeg


### Create folders

def create_folders(output_p):
	artist = album_infos[0]
	album = album_infos[1]
	output_p = output_p + '/' if output_p else ''

	if not os.path.exists(output_p + artist):
		os.makedirs(output_p + artist)

	if not os.path.exists(output_p + artist + '/' + album):
		os.makedirs(output_p + artist + '/' + album)

	output_path = output_p + artist + '/' + album + '/'



### Prepare data

def prepare_data(cue_file):
	data = []

	# Open and read cue file
	with open(cue_file, 'r') as file:
		lines = file.readlines()

	# Fill data list with lines
	for line in lines:
		line = line.strip()

		if line != '':
			if re.search('[0-9]{2}:', line): # Search for line which contains time
				data.append(line.split(' '))
			else:
				data.append(line)

	# Split data in different lists
	for index, value in enumerate(data):
		if type(value) == list:
			cue.append([value, data[index + 1]])

		if str(value).lower() == 'artist':
			album_infos.append(data[index + 1])

		if str(value).lower() == 'album':
			album_infos.append(data[index + 1])

	# print(data)
	# print(cue)
	# print(album_infos)



### Calculates duration of track

def calc_duration(start, end):
	t1 = start.split(':')
	t2 = end.split(':')
	s1 = int(t1[0]) * 60 + int(t1[1])
	s2 = int(t2[0]) * 60 + int(t2[1])
	d = s2 - s1

	return str(d)



### Prefixes numbers lower then 10 with a '0'

def num_zero_prefix(cnt):
	if cnt < 10:
		cnt = '0' + str(cnt)
	else:
		cnt = cnt

	return cnt



### Prepare ffmpeg

def convert_audio(source):
	for index, value in enumerate(cue):
		output = '"' + output_path + str(num_zero_prefix(index + 1)) + ' - ' + value[1] + '.mp3"'
		cmd = ['ffmpeg', '-nostdin', '-y']

		# Start time
		cmd.append('-ss')
		cmd.append(value[0][0])

		# Input file
		cmd.append('-i')
		cmd.append('"' + source + '"')

		# Duration
		if len(value[0]) == 2:
			cmd.append('-t')
			cmd.append(calc_duration(value[0][0], value[0][1]))

		cmd.append(output)

		# print(cmd)

		print GREEN + "Creating " + output + NC
		p_ffmpeg = subprocess.Popen(cmd)
		p_ffmpeg.wait()



### Process

def process(args):
	prepare_data(args.cue_file)
	create_folders(args.output)
	convert_audio(args.audio_source.strip())

# 	file = open(album_infos, "r")
# 	track_list = file.read()
# 	file.close()

# 	lines = track_list.split("\n")
# 	for idx, line in enumerate(lines):
# 		track_info = line.split(";")
# 		start_time = track_info[0]
# 		duration = calc_duration(track_info[0], track_info[1])
# 		filename = track_info[2]
# 		output = str(num_zero_prefix(idx + 1)) + " - " + str(filename) + ".mp3"

# 		cmd = ["ffmpeg", "-nostdin", "-y"]

# 		# ffmpeg log output
# 		cmd.append("-loglevel")

# 		if args.error:
# 			cmd.append("error")
# 		else:
# 			cmd.append("quiet")

# 		# start time of clip
# 		cmd.append("-ss")
# 		cmd.append(str(start_time))

# 		# input file
# 		cmd.append("-i")
# 		cmd.append(audio_source)

# 		# duration of clip
# 		if duration != "":
# 			cmd.append("-t")
# 			cmd.append(str(duration))

# 		# output file
# 		cmd.append(output)
		
# 		# frun fmpeg subprocess
# 		p_ffmpeg = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

# 		print GREEN + "Creating " + output + NC
		
# 		p_ffmpeg.wait()

### Main

def main():
	parser = argparse.ArgumentParser(description="With makelp you can extract audio clips from an audio-source. That source can be a ripped audio-track from a YoutTube video. All track infos, like start-time, end-time and song name, need to be in a seperate text file. Look for a detailed help at https://github.com/horstfreigang/makelp.", add_help=False)

	required = parser.add_argument_group("Required arguments");
	required.add_argument("-i", "--input", dest="audio_source", metavar="", help="Audio source file.", type=str, required=False)
	required.add_argument("-c", "--cue", dest="cue_file", metavar="", help="Plain text file with album and track infos.", type=str, required=False)

	optional = parser.add_argument_group('Optional arguments');
	optional.add_argument("-h", "--help", action="help", help="Show this help message.")
	optional.add_argument("-o", "--output", dest="output", metavar="", help="Path to where the tracks are saved. If no output is given all files will be saved in the current directory.", type=str)
	# optional.add_argument("-C", "--cover", help="Image file for the album cover.", dest="cover", metavar="", type=str, default="")
	# optional.add_argument("-I", "--id3", metavar="", help="Write ID3v2 tags in output files.")
	# optional.add_argument("-e", "--error", dest="error", metavar="", help="Print ffmpeg errors.", default=False)

	parser.set_defaults(func=process)
	args = parser.parse_args()
	args.func(args)

if __name__ == "__main__":
	main()