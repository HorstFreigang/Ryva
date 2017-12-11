#!/bin/sh

source_file=$1 # audio source file
album_infos=$2 # album and tracklist infos
count=0 # counter
orgIFS="$IFS" # default internal field separator
IFS=";" # new internal field separator
error=0 # error

# text colors
RED="\033[0;31m"
GREEN="\033[0;32m"
BROWN="\033[0;33m"
NC="\033[0m"

# album infos
artist=""
album=""
genre=""
year=""

# checks if all inputs are made and readable

if [ -z "$1" ]; then
	echo "${RED}Bitte eine Quelldatei angeben.${NC}"
	error=1
fi

if [ -z "$2" ]; then
	echo "${RED}Bitte eine Track-Liste angeben.${NC}"
	error=1
fi

if [ ! -r "$source_file" ]; then
	echo "${RED}Fehler beim Lesen der Quelldatei.${NC}"
	error=1
fi

if [ ! -r "$album_infos" ]; then
	echo "${RED}Fehler beim Lesen der Track-Liste.${NC}"
	error=1
fi

# prefixes numbers lower then 10 with a '0'

num_zero_prefix()
{
	if [ $1 -lt 10 ]; then
		num="0$1"
	else
		num=$1
	fi

	echo $num
}

# gets default album information

get_album_info()
{
	artist=$1
	album=$2
	year=$3
	genre=$4
}

# calculates duration of track

calc_duration()
{
	if [ -n "$2" ]; then
		saveIFS="$IFS"
		IFS=":"

		t1=($1)
		t2=($2)
		s1=$(((${t1[0]} * 60) + ${t1[1]}))
		s2=$(((${t2[0]} * 60) + ${t2[1]}))
		d=$(($s2 - $s1))

		IFS="$saveIFS"

		dura="-t $d"
	else
		dura=""
	fi

	echo $dura
}

# creates audio track

create_track()
{
	duration=$(calc_duration $2 $3)
	track_number=$(num_zero_prefix $1)
	cmd="ffmpeg -loglevel quiet -y -nostdin -ss $2 -i \"$source_file\" $duration \"$track_number - $4.mp3\""

	echo "${GREEN}Erstelle Titel $track_number : $4${NC}"
	echo "${BROWN}$cmd${NC}"

	eval $cmd

	wait

	add_id3_tags $4 $track_number
}

# adds id3v2 tags

add_id3_tags()
{
	cmd="id3v2 --artist \"$artist\" --album \"$album\" --song \"$1\" --genre \"$genre\" --year \"$year\" --track \"$2\" --APIC \"./cover.jpg\" \"$2 - $1.mp3\""

	echo $cmd

	eval $cmd
}

# main loop

if [ "$error" = 0 ]; then
	while read line
	do
		if [ $count = 0 ]; then
			get_album_info $line
		else
			create_track $count $line
		fi

		count=$((count + 1))
	done < "$album_infos"
fi