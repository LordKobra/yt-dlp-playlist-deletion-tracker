# yt-dlp-playlist-deletion-tracker

Prototype for keeping track of videos which got deleted from your playlists.

## Description
The internet is ephemeral. Some YouTube videos get deleted or set to private over the years and it is hard to keep track of the deleted videos when managing your own playlists. 
Youtube's own tools do not provide convenient information, so I wrote a small prototype script which allows to scan all your current playlists and compares the current scan with past scans to find deleted videos. 
Starting with the first scan, a database is built and you will be able to find deletions happening after the first scan.


The script is just a prototype and I do not plan on maintaining it beyond personal use. But the MIT license allows everyone to fork and improve upon the prototype.

## Requirements
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Python 3.10
  - Python libraries: pandas
 
## How to use?

1) Editing your account settings.

   I) Open `getplaylists.py` in a text editor.
   
   II) In line 7, you need to edit your channel name. E.g., if my YouTube channel was `@LordKobra`, the line would be `channel_name = "@LordKobra"`
   
   III) In line 8, you need to edit the commandline parameter, which supplies the login cookies to `yt-dlp`. Check [yt-dlp](https://github.com/yt-dlp/yt-dlp) for possible commandline parameters. Typical are `--cookies-from-browser BROWSER` or `--cookies FILE`. Without cookies you won't be able to keep track of your private playlists.

2) Run `python getplaylists.py` from the commandline.

The executable needs read and write permissions for the directory.

3) The resulting list of deletions will be saved to the "deletion_logs" sub-folder.

The database is in the "database" sub-folder. Please do not delete it, because you will need it for future scans.

For maximum backwards compatibility, I would also recommend to NOT delete files in the "playlist_overview" and "playlist" folder.
