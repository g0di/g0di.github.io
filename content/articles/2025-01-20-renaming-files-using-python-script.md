Title: Renaming files using Python script
Tags: python, script
Description: Discover my new Python project providing a small script for easily renaming one or several files or directories using regular expressions

Lately, I wanted to rename lot of files and directories on my personal server, in particular media like TV Shows episodes. As there was lot of files I decided to look for an UNIX command to ease my burden.
Unfortunately, I could not find such command on my server (a Synology NAS) and was unable to figure out how to install additional packages on it so I decided to build my own `rename` command using a Python script.

You can find the project repository and documentation [here](https://github.com/g0di/rename). Nothing rocket science out there, the whole code largely fit into a single file.
I mainly made this for myself and use a proper project layout to facilitate future updates (if any) and script installation.
> I wanted to avoid to have to copy paste my script to my server on each changes.

You can install it using `uv` or `pipx` (as documented) directly using the git repository URL which is very convenient and prevents me to release it on Pypi (as I'm not expecting lot of people to actually use it).

I personally installed `uv` on my NAS for my admin account which greatly ease using various Python versions without impacting the system as well as installing Python tools.
I then installed my `rename` script using `uv` allowing me to use my rename command when logged as admin through SSH.

The script use Python regular expressions to do replacements allowing to use capture groups which is super handy when you want to rename a large amount of TV show episodes using a same pattern.

For example, imagine you've got all episodes of the first season of **Squid Game** in a `Squid Game (2021)/Season 01/` directory and named like: `squid game - 01 - <episode title>.mkv` and you want to format them for being recognized properly by, let's say, Plex.
```bash
rename "./Squid Game (2021)/Season 01/*.mkv" \
       'squid game - (\d\d) - (.*)\.mkv' \
       'Squid Game (2021) - s01e\1 - \2.mkv'
```

- `"./Squid Game (2021)/Season 01/*.mkv"` The first argument select all `.mkv` files as candidates for rename
- `'squid game - (\d\d) - (.*)\.mkv'` The second argument is the substring that has to be replaced. Here we use a regular expression with capture groups to capture the episode number and title
- `'Squid Game (2021) - s01e\1 - \2.mkv'` The third argument is the replacement substring. We use capture groups (`\1`, `\2`) to produces a new name reusing the episode and title we captured

Considering the first episode is named like `squid game - 01 - Red Light, Green Light.mkv`, it will be renamed as `Squid Game (2021) - s01e01 - Red Light, Green Light.mkv`

The fact that the second argument is considered as a regular expression by default can be misleasing. Maybe in the future I'll do the switch and add a dedicated flag to turns explicitly indicates that we are using a regular expression. This would prevent from having to escape special characters (like `.`) for simple use cases.
