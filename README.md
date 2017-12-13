## What is MakeLP?
MakeLP is a little script which extracts clips from an (audio) source-file and saves them as seperate audio files.

## Prerequisites
For MakeLP to work you need to have `ffmpeg` installed.
If you want MakeLP to write ID3v2-tags then you need `id3v2` as well.

## Usage
`makelp -i AUDIO-SOURCE -t TRACKLIST`

## Options
### Required
`-i`: Input file. Should be an audio-file like WEBM or M4A.  
`-t`: Text file with informations for each track, like start and end time and song name.