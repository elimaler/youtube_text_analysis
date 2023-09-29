# youtube_text_analysis
A repo for analysis the content of youtube channels transcriptions.

This repo is for the analysis of youtube channel transcriptions. It works to download all transcriptions from a channel and then allows the user to keyword search. Data is stored locally.

## Method

This script has three main methods. Details can be found by running python3/src main.py --help.

1. download: a function to download all available transcripts with the channels URL
2. update: a function to update all existing channels with new transcripts.
3. search: a function to search in downloaded text for keyword matches.

Each function has arguments allowing specification of where to store files, whether or not to skip existing files. In the case of the search it allows control of size of window and which channels to search in.
