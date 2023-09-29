from youtube_transcript_api import YouTubeTranscriptApi
import scrapetube
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import requests
import json
import os
import datetime

# this function will get the text of transcripts from from a channel id
# - it sub functions get the list of videos and then through multi threading pull the text
def getChannelTranscripts(channel_id: str, skip_list: list, video_type: str='all'):
    # get list of all videos
    all_videos = getVideoList(channel_id, video_type)
    all_videos.reverse()
    # remove videos that have already been retrieved
    all_videos = [x for x in all_videos if x[0] not in skip_list]
    # all_videos = all_videos
    # multithread all videos to get the transcripts
    texts = multithreaded_transcripts([x[0] for x in all_videos])
    texts = {x[0]:x[1] for x in texts}

    # return the text and video info
    results = [(x, texts[x[0]]) for x in all_videos if texts[x[0]]]

    return results

# get video list uses the API to get all the videos on a channel with channel
# this is called by getChannelTranscripts
def getVideoList(channel_id: str, video_type: str):
    # check that the video types are in allowed types    
    allowed_types = ['videos', 'shorts', 'streams']
    if video_type == "all":
        video_type = allowed_types
    if type(video_type) != list:
        video_type = [video_type]
    try:
        assert sum([x in allowed_types for x in video_type])
    except:
        raise Exception(f"video_type must be in {allowed_types} or 'all'")
        
    # create a dictionary
    results = {vid:None for vid in video_type}
    for v_type in video_type:
        # retrieve all video ID's with channel ID
        videos = scrapetube.get_channel(channel_id,content_type=v_type, sleep=0.2)
        results[v_type] = videos

    all_videos = []

    # pull out videoID and title from the video info
    for v_type in results:
        videos = results[v_type]
        for video in videos:
            vid_id = video['videoId']
            title = video['title']['runs'][0]['text']
            all_videos.append((vid_id, title, v_type))
    # return results
    return all_videos


# this function gets the transcript of a video from youtube's API
# it is called in multithreaded_transcripts function
def make_transcript(video_id, verbose=False):
    # try and get the transcript
    try:
        text = YouTubeTranscriptApi.get_transcript(video_id)
        return (video_id, text)
    # if there is no transcript return nothing
    except Exception as e:
        if verbose:
            print(f"No transcript for {video_id}")
        return None


# this function handles the multithreading of transcript creations
# it is called in getChannelTranscripts
def multithreaded_transcripts(video_ids, num_threads=100, verbose=False):
    # create an empty array for transcripts
    transcripts = []
    # start multithreading
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # prepare dictionary for extraction
        future_to_id = {executor.submit(make_transcript, video_id, verbose): video_id for video_id in video_ids}
        # run multithreading
        for future in concurrent.futures.as_completed(future_to_id):
            video_id = future_to_id[future]
            try:
                transcript = future.result()
                if transcript is not None:
                    transcripts.append(transcript)
                else:
                    transcripts.append([video_id, None])
            except Exception as e:
                if verbose:
                    print(f"Error occurred while processing {video_id}: {str(e)}")
                    transcripts.append([video_id, None])
    # return results
    return transcripts


# a function to get the channel ID from url 
def getChannelID(url):
    response = requests.get(url)
    channel_id = response.text.split("https://www.youtube.com/channel/")[1].split('"')[0]
    return channel_id

def dumpData(channel_id, results, log, data_location):

    loc = data_location+"youtube_analysis_data/"+channel_id +"/"
    # update the log
    if channel_id not in log:
        log[channel_id] = {}
        log[channel_id]['videos'] = {}
        if not os.path.exists(loc):
            os.makedirs(loc)
    log[channel_id]['updated'] = str(datetime.datetime.now())
    for x in results:
        temp = bool(x[1])
        log[channel_id]['videos'][x[0][0]]=temp
    
    # save info
    # create the directory if it doesn't exist

    for x in results:
        res = buildDoc(x)
        with open(loc+x[0][0]+".txt", "w") as file:
            file.write(res)
    return log

# a function to download a new channel from a URL
# this should check if it exidsts in the current "DB"
def updateChannelCorpus(channel_url, data_location="./", skip_existing=False, verbose=False):
    # try and open the log file
    if os.path.exists(data_location+"youtube_analysis_data/"):
        try:
            log = json.load(open(data_location+"youtube_analysis_data/log.json", "r"))
        # if there is no directory then create a new directory
        except:
            # create an empty log dictionary
            log = {}
    else:
        print("No directory found, creating at data location.")
        os.makedirs(data_location+"youtube_analysis_data/")
        log = {}
    # get the channel ID
    channel_id = getChannelID(channel_url)
    print(f"CHANNEL_ID: {channel_id}")
    # if skip_existing is true and the channel id is in the log
    if channel_id in log and skip_existing:
        # get videos to skip
        skip_videos = [x for x in log[channel_id]['videos']]
    else:
        skip_videos = []
    
    
    # get results
    results = getChannelTranscripts(channel_id, skip_videos)
    log = dumpData(channel_id, results, log, data_location)
    json.dump(log, open(data_location+"youtube_analysis_data/log.json", "w"))
    return


# a function for updating the existing corpus
def updateCorpus(data_location="./", skip_existing=True):
    try:
        log = json.load(open(data_location+"youtube_analysis_data/log.json"))
    except:
        raise Exception("No log exists")
    
    for channel_id in log:
        if skip_existing:
            skip_videos = [x for x in log[channel_id]['videos']]
        else:
            skip_videos = []
        print(f"CHANNEL_ID: {channel_id}")
        results = getChannelTranscripts(channel_id, skip_videos)
        log = dumpData(channel_id, results, log, data_location)
    
    json.dump(log, open(data_location+"youtube_analysis_data/log.json", "w"))


def buildTranscriptTimes(transcript):
    text = []
    times = []
    index = 0
    for x in transcript:
        text.append(x['text'])
        times.append([index,x['start']])
        index += len(x['text'])+1
    return " ".join(text), str(times)


def buildDoc(x):
    text, times = buildTranscriptTimes(x[1])

    res = ""
    res += x[0][1]
    res += "\n"
    res += x[0][0]
    res += "\n"
    res += x[0][2]

    res += "\n\n\n#TEXT:\n\n\n"
    res += text
    res += "\n\n\n#TIMES\n\n\n" 
    res += times

    return res
