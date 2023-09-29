import json
import sys
import os
import csv

def searchKwd(channel_id, kwd, data_location = "./", window=100, save=False):
    log = json.load(open(data_location+"youtube_analysis_data/log.json", "rb"))
    if channel_id == None:
        for x in log:
            searchKwd(x, kwd, data_location, window=window, save=save)
        return

    loc = data_location + "youtube_analysis_data/" + channel_id + "/"
    # check the channel_id has been downloaded
    if channel_id not in log:
        raise Exception("No data for this channel.")
    else:
        channel = log[channel_id]['videos']
    
    # prepare some arays
    corpus_text = []
    corpus_times = []
    corpus_titles = []
    output = [["keyword", "channel_id", "video_id", "video_title", "time_code", "link", "text"]]
    if save:
        if not os.path.exists(data_location + "youtube_analysis_data/searchResults/"):
            os.mkdir(data_location + "youtube_analysis_data/searchResults/")
        file = open(data_location + f"youtube_analysis_data/searchResults/{kwd}_{channel_id}.txt", "w")
        sys.stdout = file
    

    # iter through all videos
    for x in channel:

        if not channel[x]:
            continue
        with open(loc+x+".txt", "r") as file:
            text = file.read()
        video_id = text.split("\n")[1]
        video_title = text.split("\n")[0]
        title = video_title + " | " + video_id
        transcript = text.split("\n\n\n")[2]
        times = eval(text.split("\n\n\n")[-1])
        corpus_text.append(transcript)
        corpus_times.append(times)
        corpus_titles.append(title)

        # search for kwd:
        if kwd in transcript:
            print("|"+3*"---"+" "+title+" " + 3*"---"+"|")
            print("\n")
            windows = get_occurances(kwd, transcript, window)
            for w in windows:
                index = w[0]
                for i,x in enumerate(times):
                    
                    if x[0] > index:
                        time = times[i-1][1]
                        hours, remainder = divmod(time, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        time_pretty = f'{(int(hours))}:{int(minutes):02d}:{int(seconds):02d}'
                        print("TIME:", time_pretty)
                        link = f"https://www.youtube.com/watch?v={video_id}&t={int(time)}"
                        print("WATCH:", link)
                        break
                transcript_window = transcript[w[0]:w[1]]
                row = [kwd, channel_id, video_id, video_title, time_pretty, link, transcript_window]
                output.append(row)
                print(transcript_window)
                print("\n")
    if save:
        file.close()
        with open(data_location + f"youtube_analysis_data/searchResults/{kwd}_{channel_id}.csv", "w", newline="") as csv_file:
            csv_file = csv.writer(csv_file)
            csv_file.writerows(output)


        


def get_occurances(kwd, transcript, window):
    # create an empty list of indices
    indices = []
    # find all occurances of the keyword
    index = transcript.find(kwd)
    while index != -1:
        indices.append(index)
        index = transcript.find(kwd, index + 1)
    # create a groups array to keep track of which group
    groups = [0 for x in indices]
    groups_list = {}
    # iterate through indices
    for i,x in enumerate(indices):
        # the index is not in a group make a new group
        if groups[i] == 0 :
            groups[i] = max(groups)+1
            groups_list[groups[i]]=[x]
        # if this is the final index skip it now
        if i >= len(indices)-1:
            continue
        # check if the next index is within the window
        if indices[i+1]-x < window:
            # iif it is add it to this group
            groups[i+1]=groups[i]
            groups_list[groups[i]].append(indices[i+1])
    
    # now iterate through the groups
    windows = []

    for x in groups_list:
        # find the lowest and highest minus the window
        lower = min(groups_list[x])-window
        upper = max(groups_list[x])+window
        # add this window
        windows.append([lower,upper])
    return windows
