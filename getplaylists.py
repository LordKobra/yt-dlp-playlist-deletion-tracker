import os
import pandas
import pathlib
import datetime

# USER VARIABLES
channel_name = "@MyChannelName"
cookies = "--cookies-from-browser firefox"
# END OF USER VARIABLES

def download_playlists(download_time):
    # Create the list of playlists
    os.system("yt-dlp"
              " --verbose"
              " --dump-json"
              " --flat-playlist"
              f" {cookies}"
              f" -v \"https://www.youtube.com/{channel_name}/playlists?view=1&sort=dd&shelf_id=0\""
              f" > \"playlist_overview/playlists_{download_time}.txt\"")

    playlists_db = pandas.read_json(
        f"playlist_overview/playlists_{download_time}.txt", lines=True)

    # Download the video titles of each playlist
    for index, row in playlists_db.iterrows():
        os.system("yt-dlp"
                  " --dump-json"
                  " --flat-playlist"
                  f" {cookies}"
                  f" -v \"{row.url}\" "
                  f" > \"playlists/{row.title}_{download_time}.txt\"")

    return


def organize_playlists(main_path):

    playlist_path = main_path.joinpath("playlists")
    db_path = main_path.joinpath("database")

    # find unique playlist names
    files = os.listdir(playlist_path)
    playlist_dict = {}
    for file in files:
        playlist_title = "_".join(file.split("_")[:-1])
        playlist_dict[playlist_title] = 1
    playlist_names = list(playlist_dict.keys())

    # do we read from db first in case the history is deleted?
    # or straight up from history, overwriting db? -> read db first
    db_list = os.listdir(db_path)
    for playlist_name in playlist_names:
        db_name_full = playlist_name + ".txt"
        playlist_db = pandas.DataFrame({
            'title': pandas.Series(dtype='str'),
            'url': pandas.Series(dtype='str'),
            'added_date': pandas.Series(dtype='str'),
            'last_date': pandas.Series(dtype='str'),
            'removed': pandas.Series(dtype='bool'),
            'duration_string': pandas.Series(dtype='str'),
            'channel': pandas.Series(dtype='str'),
            'channel_id': pandas.Series(dtype='str'),
            'playlist_index': pandas.Series(dtype='int64')})

        if db_name_full in db_list:
            playlist_db = pandas.read_json(os.path.join(db_path, db_name_full))
            playlist_db = playlist_db.reset_index(drop=True)

        # find all corresponding logs
        playlist_dates = []
        playlist_dates_dict = {}
        for file in files:
            playlist_title = "_".join(file.split("_")[:-1])
            if playlist_name == playlist_title:
                playlist_date_str = file.split("_")[-1][:-4]
                playlist_date = datetime.datetime.strptime(
                    playlist_date_str, '%d.%m.%y-%H:%M:%S')
                playlist_dates.append(playlist_date)
                playlist_dates_dict[playlist_date] = playlist_date_str

        playlist_dates = sorted(playlist_dates)
        max_date = datetime.datetime(2000, 1, 1, 1, 1, 1)

        # read all logs of playlist_name
        for playlist_date in playlist_dates:
            max_date = max(max_date, playlist_date)
            file_name: str = playlist_name + "_" + \
                playlist_dates_dict[playlist_date] + ".txt"
            record_db = pandas.read_json(os.path.join(
                playlist_path, file_name), lines=True)
            # compare each entry of the record_db with playlist_db and add or removedate
            for row in record_db.itertuples():
                if row.url in playlist_db["url"].values:
                    row_idx = playlist_db.loc[playlist_db["url"]
                                              == row.url].index[0]
                    playlist_db.at[row_idx,
                                   "last_date"] = playlist_dates_dict[playlist_date]
                else:
                    # index can be NaN, but max() evaluates to first argument in comparison
                    # -> 0 in this case
                    playlist_db.loc[max(0, playlist_db.index.max()) + 1] = {
                        "title": row.title,
                        "url": row.url,
                        "added_date": playlist_dates_dict[playlist_date],
                        "last_date": playlist_dates_dict[playlist_date],
                        "removed": False,
                        "duration_string": row.duration_string,
                        "channel": row.channel,
                        "channel_id": row.channel_id,
                        "playlist_index": row.playlist_index}

        # check removed
        for i in playlist_db.index:
            last_date = datetime.datetime.strptime(
                playlist_db.loc[i]["last_date"], '%d.%m.%y-%H:%M:%S')
            if (last_date < max_date):
                playlist_db.at[i, "removed"] = True

        # save
        playlist_db.to_json(os.path.join(db_path, db_name_full))
    return


def print_deleted(main_path, current_date):
    db_path = main_path.joinpath("database")

    # find unique playlist names
    playlist_names = os.listdir(db_path)

    # print outliers
    with open(f"deletion_logs/deleted_{current_date}.txt", "w") as f:
        for playlist_name in playlist_names:

            playlist_db = pandas.read_json(
                os.path.join(db_path, playlist_name))
            playlist_db = playlist_db.reset_index(drop=True)

            removed_db = playlist_db.loc[playlist_db.removed == True]
            if not removed_db.empty:
                f.write(playlist_name[:-4] + "\n")
                f.write(removed_db.to_string())
                f.write("\n\n\n")
    return


if __name__ == '__main__':
    # set cwd to filepath, so we got consistent folder structure
    main_path = pathlib.Path(__file__).parent.resolve()
    os.chdir(main_path)
    print("Current Working Directory: \'" + str(main_path.resolve()) + "\'")

    # fetch date inside python
    download_time = datetime.datetime.now()
    download_time = download_time.strftime('%d.%m.%y-%H:%M:%S')
    print("Download time " + download_time)

    # create folders
    os.makedirs(main_path.joinpath("playlist_overview"), exist_ok=True)
    os.makedirs(main_path.joinpath("playlists"), exist_ok=True)
    os.makedirs(main_path.joinpath("database"), exist_ok=True)
    os.makedirs(main_path.joinpath("deletion_logs"), exist_ok=True)

    download_playlists(download_time)
    organize_playlists(main_path)
    print_deleted(main_path, download_time)

