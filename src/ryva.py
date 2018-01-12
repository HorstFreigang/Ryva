#! /usr/bin/env python3

import os, sys, re, time, argparse, subprocess
from mutagen.id3 import ID3, TALB, TYER, TCON, TCMP, TRCK, TPE1, TIT2, APIC

output_path = ''
dict_cue = {
	'compilation': 0,
	'album': '',
	'artist': '',
	'genre': '',
	'year': '',
	'songs': []
}

# Text colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
BROWN = '\033[0;33m'
NC = '\033[0m'



### Create folders

def create_folders(output_p):
	global output_path

	artist = ''

	artist = dict_cue['artist']
	album = dict_cue['album']

	output_p = output_p + '/' if output_p else ''

	if not os.path.exists(output_p + artist):
		os.makedirs(output_p + artist)

	if not os.path.exists(output_p + artist + '/' + album):
		os.makedirs(output_p + artist + '/' + album)

	output_path = output_p + artist + '/' + album + '/'



### Prepare data

def prepare_data(cue_file):
	f = open(cue_file, 'r')
	lines = f.readlines()
	f.close()

	for i, line in enumerate(lines):
		line = line.strip()

		if re.match('#compilation', line):
			dict_cue['compilation'] = 1

		if re.match('#album', line):
			dict_cue['album'] = lines[i + 1].strip()

		if re.search('#artist', line):
			dict_cue['artist'] = lines[i + 1].strip()

		if re.match('#genre', line):
			dict_cue['genre'] = lines[i + 1].strip()

		if re.match('#year', line):
			dict_cue['year'] = lines[i + 1].strip()

		if re.match('\d{2}:', line):
			if (i + 2) < len(lines):
				if lines[i + 2].strip():
					dict_cue['songs'].append([convert_to_sec(line.split(' ')), lines[i + 1].strip(), lines[i + 2].strip()])
				else:
					dict_cue['songs'].append([convert_to_sec(line.split(' ')), lines[i + 1].strip()])

	# print(dict_cue)



### Download audio using youtube-dl

def download(url):
	cmd = ['youtube-dl', '-o', output_path + 'ryva_dl_file.%(ext)s', '-f', 'bestaudio[ext=m4a]', url]

	p_dl = subprocess.Popen(cmd)
	p_dl.wait()



### Calculates duration of track

def calc_duration(start, end):
	# t1 = start.split(':')
	# t2 = end.split(':')
	# s1 = int(t1[0]) * 60 + int(t1[1])
	# s2 = int(t2[0]) * 60 + int(t2[1])
	# d = s2 - s1
	d = int(end) - int(start)

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
	if type(time) == list:
		d1 = time[0].split(':')
		if len(d1) == 3:
			s1 = int(d1[0]) * 3600 + int(d1[1]) * 60 + round(float(d1[2]), 0)
		else:
			s1 = int(d1[0]) * 60 + round(float(d1[1]), 0)

		d2 = time[1].split(':')
		if len(d2) == 3:
			s2 = int(d2[0]) * 3600 + int(d2[1]) * 60 + round(float(d2[2]), 0)
		else:
			s2 = int(d2[0]) * 60 + round(float(d2[1]), 0)

		return [int(s1), int(s2)]

	else:
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
			print('  | ' + '#' * bar + '-' * (max_bar_width - bar) + ' | ' + str(percentage) + ' %', end='\r', flush=True)



### Prepare ffmpeg

def convert_audio(source, cover):
	for i, value in enumerate(dict_cue['songs']):
		if dict_cue['compilation']:
			file_name = re.sub('/', '_', value[1]) + ' - ' + re.sub('/', '_', value[2]) + '.mp3'
		else:
			file_name = re.sub('/', '_', value[1]) + '.mp3'

		output = output_path + str(num_zero_prefix(i + 1)) + ' - ' + file_name
		cmd = ['ffmpeg', '-y', '-loglevel', 'verbose']

		# Start time
		cmd.append('-ss')
		cmd.append(str(value[0][0]))

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

		# add_id3_tags(i, output, cover)



### ID3v2 tags

def add_id3_tags(t, file, cover):
	audio = ID3(file)

	# album
	audio.add(TALB(encoding=3, text=u'' + dict_cue['album']))

	# genre
	audio.add(TCON(encoding=3, text=u'' + dict_cue['genre']))

	# year
	audio.add(TYER(encoding=3, text=u'' + dict_cue['year']))

	# compilation
	audio.add(TCMP(encoding=3, text=u'' + str(dict_cue['compilation'])))

	# track number
	audio.add(TRCK(encoding=3, text=u'' + str(t+1) + '/' + str(len(dict_cue['songs']))))

	# artist
	if len(dict_cue['songs'][t]) == 3:
		audio.add(TPE1(encoding=3, text=u'' + dict_cue['songs'][t][1]))
	else:
		audio.add(TPE1(encoding=3, text=u'' + dict_cue['artist']))

	# song title
	if len(dict_cue['songs'][t]) == 3:
		audio.add(TIT2(encoding=3, text=u'' + dict_cue['songs'][t][2]))
	else:
		audio.add(TIT2(encoding=3, text=u'' + dict_cue['songs'][t][1]))

	# cover
	if cover:
		audio.add(APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=open(cover, 'rb').read()))

	audio.save()



### Process

def process(args):
	prepare_data(args.cue_file)
	create_folders(args.output)

	if re.search('http', args.audio_source):
		download(args.audio_source)
		convert_audio(output_path + 'ryva_dl_file.m4a', args.id3_cover)
	else:
		convert_audio(args.audio_source.strip(), args.id3_cover)



### Main

def main():
	parser = argparse.ArgumentParser(description='With Ryva you can extract audio clips from an audio-source. That source can be a ripped audio-track from a YoutTube video. All track infos, like start-time, end-time and song name, need to be in a seperate text file. Look for a detailed help at https://github.com/HorstFreigang/Ryva.', add_help=False)

	required = parser.add_argument_group('Required arguments');
	required.add_argument('-i', '--input', dest='audio_source', metavar='', help='Audio source file or URL.', type=str, required=True)
	required.add_argument('-c', '--cue', dest='cue_file', metavar='', help='Plain text file with album and track infos. See *URL* for more information.', type=str, required=True)

	optional = parser.add_argument_group('Optional arguments');
	optional.add_argument('-h', '--help', action='help', help='Show this help message.')
	optional.add_argument('-o', '--output', dest='output', metavar='', help='Path to where the tracks are saved. If no output is given all files will be saved in the current directory.', type=str)
	optional.add_argument('-C', '--cover', dest='id3_cover', metavar='', help='Path to image file, which should be used as an attachment image. Should be an JPEG.')

	parser.set_defaults(func=process)
	args = parser.parse_args()
	args.func(args)

if __name__ == '__main__':
	main()