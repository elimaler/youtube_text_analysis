import argparse
import getData
import textAnalysis

def download(args):
    data_location = args.data_location
    url = args.url
    skip_existing = args.skip_existing
    # Your download logic here
    print(f"Downloading: {url}")
    getData.updateChannelCorpus(url, data_location, skip_existing)

def update(args):
    data_location = args.data_location
    skip_existing = args.skip_existing
    # Your update logic here
    print(f"Updating...")
    getData.updateCorpus(data_location, skip_existing)

def search(args):
    data_location = args.data_location
    channel_id = args.channel_id
    keyword = args.keyword
    window_size = args.window_size
    # Your search logic here
    textAnalysis.searchKwd(channel_id, keyword, data_location, window_size)

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="A script for downloading and searching through youtube transcripts..")

    # Add a common argument for data_location
    parser.add_argument("--data_location", type=str, default="./", help="Data location (default: ./)")

    # Add subparsers for different commands (-download, -update, -search)
    subparsers = parser.add_subparsers(dest="command", title="commands", description="Available commands", required=True, metavar="COMMAND")

    # Subparser for the -download command
    download_parser = subparsers.add_parser("download", help="Download videos")
    download_parser.add_argument("url", type=str, help="URL of homepage of channel to download")
    download_parser.add_argument("--skip_existing", action="store_false", default=True, help="Skip existing downloaded videos")

    # Subparser for the -update command
    update_parser = subparsers.add_parser("update", help="Update videos")
    update_parser.add_argument("--skip_existing", action="store_false", default=True, help="Skip exostomg downloaded videos")

    # Subparser for the -search command
    search_parser = subparsers.add_parser("search", help="Search videos")
    search_parser.add_argument("keyword", type=str, help="Keyword to search for")
    search_parser.add_argument("--channel_id", type=str, default=None, help="Channel ID (leave blank for all channels)")
    search_parser.add_argument("--window_size", type=int, default=100, help="Window size (default: 100)")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the appropriate function based on the selected command
    if args.command == "download":
        download(args)
    elif args.command == "update":
        update(args)
    elif args.command == "search":
        search(args)

if __name__ == "__main__":
    main()
