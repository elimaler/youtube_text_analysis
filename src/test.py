import getData
import scrapetube
channel_id = "UC7wQcpV9nhGFn89VxixwePA"

videos = scrapetube.get_channel(channel_id,sleep=0.2)

for x in videos:
    print(x)
    break