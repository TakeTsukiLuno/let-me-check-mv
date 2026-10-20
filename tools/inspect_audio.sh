#!/bin/sh
ffprobe -v error -show_entries format=duration -show_entries stream=codec_name,sample_rate,channels,bits_per_raw_sample -of json "$(dirname "$0")/../assets/audio/MV_MASTER_48k_24bit_-14LUFS.wav"
