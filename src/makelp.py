#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, re, time, argparse, subprocess

cue = []
album_infos = []
output_path = ''

# text colors

RED = '\033[0;31m'
GREEN = '\033[0;32m'
BROWN = '\033[0;33m'
NC = '\033[0m'



### Create folders

def create_folders(output_p):
	global output_path

	artist = album_infos[0][1]
	album = album_infos[1][1]
	output_p = output_p + '/' if output_p else ''

	if not os.path.exists(output_p + artist):
		os.makedirs(output_p + artist)

	if not os.path.exists(output_p + artist + '/' + album):
		os.makedirs(output_p + artist + '/' + album)

	output_path = output_p + artist + '/' + album + '/'



### Prepare data

def prepare_data(cue_file):
	data = []
	track_no = 0;

	# Open and read cue file
	with open(cue_file, 'r') as file:
		lines = file.readlines()

	# Fill data list with lines
	for line in lines:
		line = line.strip()

		if line != '':
			if re.search('\d{2}:', line): # Search for line which contains time
				data.append(line.split(' '))
			else:
				data.append(line)

	# Split data in different lists
	for index, value in enumerate(data):
		if type(value) == list:
			cue.append([value, data[index + 1]])
			track_no += 1
			album_infos.append([track_no, data[index + 1]])

		if str(value).lower() == 'artist':
			album_infos.append(['artist', data[index + 1]])

		if str(value).lower() == 'album':
			album_infos.append(['album', data[index + 1]])

		if str(value).lower() == 'genre':
			album_infos.append(['genre', data[index + 1]])

		if str(value).lower() == 'year':
			album_infos.append(['year', data[index + 1]])

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



### Convert to seconds

def convert_to_sec(time):
	digits = time[5:].split(':')
	seconds = int(digits[0]) * 3600 + int(digits[1]) * 60 + round(float(digits[2]), 0)
	
	return int(seconds)



### ffmpeg progress

def ffmpeg_progress(p, end_time):
	re_time = re.compile('time=(\d{2}):(\d{2}):(\d{2}).(\d{2})', re.I | re.U)

	max_bar_width = int(round((os.get_terminal_size().columns / 2), 0))

	while True:
		line = p.stdout.readline().strip()

		if line == '' and p.poll() is not None:
			break

		m_time = re_time.search(line)

		if m_time != None:
			percentage = int(round(100 / end_time * convert_to_sec(m_time.group(0)), 0))
			bar = int(round(max_bar_width / 100 * percentage))
			print('  0 % | ' + '#' * bar + '-' * (max_bar_width - bar) + ' | 100 %', end='\r')



### Prepare ffmpeg

def convert_audio(source, id3):
	for index, value in enumerate(cue):
		output = output_path + str(num_zero_prefix(index + 1)) + ' - ' + value[1] + '.mp3'
		cmd = ['ffmpeg', '-y', '-loglevel', 'verbose']

		# Start time
		cmd.append('-ss')
		cmd.append(value[0][0])

		# Input file
		cmd.append('-i')
		cmd.append(source)

		# Duration
		duration = calc_duration(value[0][0], value[0][1])
		cmd.append('-t')
		cmd.append(duration)

		# Output
		cmd.append(output)

		# print(cmd)

		print('Writing ' + output)

		# Run ffmpeg
		p_ffmpeg = subprocess.Popen(
				cmd,
				# shell=True,
				# stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				universal_newlines=True
			)

		# Progress bar
		ffmpeg_progress(p_ffmpeg, int(duration))

		# Wait until ffmpeg is finished
		p_ffmpeg.wait()

		# Write status
		time.sleep(1)
		sys.stdout.write('\x1b[2K') # Erease line
		print(GREEN + 'OK' + NC + '\n')

		if id3:
			add_id3_tags(value[1], output)



### ID3v2 tags

def add_id3_tags(song, file):
	cmd = ['id3v2']
	
	for value in album_infos:
		if value[0] == 'artist':
			cmd.append('--artist')
			cmd.append(value[1])

		if value[0] == 'album':
			cmd.append('--album')
			cmd.append(value[1])

		if value[0] == 'genre':
			cmd.append('--genre')
			cmd.append(value[1])

		if value[0] == 'year':
			cmd.append('--year')
			cmd.append(value[1])

		if value[1] == song:
			cmd.append('--song')
			cmd.append(song)
			cmd.append('--track')
			cmd.append(str(value[0]))

	cmd.append(file)

	# print(cmd)

	p_id3 = subprocess.Popen(cmd)



### Process

def process(args):
	prepare_data(args.cue_file)
	create_folders(args.output)
	convert_audio(args.audio_source.strip(), args.id3)



### Main

def main():
	parser = argparse.ArgumentParser(description="With makelp you can extract audio clips from an audio-source. That source can be a ripped audio-track from a YoutTube video. All track infos, like start-time, end-time and song name, need to be in a seperate text file. Look for a detailed help at https://github.com/horstfreigang/makelp.", add_help=False)

	required = parser.add_argument_group("Required arguments");
	required.add_argument("-i", "--input", dest="audio_source", metavar="", help="Audio source file.", type=str, required=False)
	required.add_argument("-c", "--cue", dest="cue_file", metavar="", help="Plain text file with album and track infos. See *URL* for more information.", type=str, required=False)

	optional = parser.add_argument_group('Optional arguments');
	optional.add_argument("-h", "--help", action="help", help="Show this help message.")
	optional.add_argument("-o", "--output", dest="output", metavar="", help="Path to where the tracks are saved. If no output is given all files will be saved in the current directory.", type=str)
	optional.add_argument("-I", "--id3", dest="id3", action='store_true', help="Write ID3v2 tags to output files. Cue-file must be in proper format. See *URL* for more information.")
	# optional.add_argument("-C", "--cover", dest="id3_cover", metavar="", help="Image file for the album cover.", type=str)
	# optional.add_argument("-e", "--error", dest="error", metavar="", help="Print ffmpeg errors.", default=False)

	parser.set_defaults(func=process)
	args = parser.parse_args()
	args.func(args)

if __name__ == "__main__":
	main()