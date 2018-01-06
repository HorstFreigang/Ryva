## What is Ryva?
Ryva is a little script which extracts clips from an audio source-file and saves them as seperate audio files.

## Prerequisites
For Ryva to work you need to have `ffmpeg` installed.
If you want Ryva to write ID3v2-tags then you need `id3v2` as well.

## Usage
`ryva -i AUDIO-SOURCE -t TRACKLIST`

## Options
### Required
`-i`, `--input`: Input file. Should be an audio-file like WEBM or M4A.  
`-c`, `--cue`: Text file with informations for each track, like start and end time and song name.

### Optional
`-o`, `--output`: Path to where the tracks are saved. If no output is given all files will be saved in the current directory.  
`-I`, `--id3`: Write ID3v2 tags to output files. Cue-file must be in proper format.

## Cue-file
The content of the cue-file needs to be in a particular format.

