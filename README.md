ASL3 Weather Announcer (ASL3_wx)

ASL3 Weather Announcer is a Python-based weather and civil-alert announcer for AllStarLink 3 (Asterisk) amateur radio nodes. It periodically checks official weather sources and, when something is issued for your area, generates a spoken announcement and plays it out over your node — no internet radio, no cloud TTS, no GPU required.

This is the lightweight, fully offline-TTS version of the project — it's built to run comfortably on a Raspberry Pi (or similar single-board computer) alongside your existing AllStarLink node software. A separate, more resource-intensive companion project handles voice-cloned announcements for people who want a more natural-sounding voice and have a machine to spare for it; this repo is for everyone else.

It provides automated verbal announcements for:

Active weather alerts — warnings, watches, and advisories, as they're issued
Scheduled reports — forecast, current conditions, sunrise/sunset and moon phase, read out on a schedule you set
Time announcements — spoken local time at the start of each report
Features
Multi-country support: National Weather Service (NWS) data for the US, Environment Canada data for Canada, with a plugin-style provider architecture so more countries can be added
Flexible location: GPS via gpsd for mobile/portable stations, or a fixed lat/lon for a permanent install
English and French announcements, with the groundwork in place for more languages
Configurable alert tone: an attention tone can play automatically ahead of Warning-level (or higher) alerts
Canada's Alert Ready system: optional support for non-weather civil emergency alerts, in addition to Environment Canada weather data
Offline TTS by default: uses pico2wave, a small, fast, fully offline speech engine that runs comfortably on a Raspberry Pi
Recommended hardware

This project is deliberately built to be easy for hams to run on hardware they probably already have.

A Raspberry Pi is the easiest path. Because the text-to-speech engine (pico2wave) runs entirely offline with no GPU or significant CPU load, this doesn't need anything more powerful than a Raspberry Pi 3B+ or 4. A great many AllStarLink nodes already run on a Pi, so in most cases you can install this directly on the same Pi that's running your node — no extra hardware needed.
Minimum practical spec: Raspberry Pi 3B+ or newer (a Pi 4 with 2GB+ RAM is a comfortable choice), a 16GB or larger SD card (Class 10 / A1 rated, or better yet a USB SSD for reliability), and a stable internet connection for polling weather data.
Other SBCs work fine too — this is plain Python with a handful of pip packages, so an Orange Pi, NanoPi, Rock Pi, or an old laptop running Linux will all work equally well. The Raspberry Pi is just the most common and best-documented option in the ham community.
If your AllStarLink node is already running close to its limits (busy with other add-ons, SDR monitoring, etc.), running this on a second, inexpensive Pi dedicated to just this task is a reasonable alternative.
Installation

This guide assumes basic comfort with the Linux command line (typing commands over SSH) but no prior Python experience.

1. Install system prerequisites

On your ASL3 server (Debian/Raspberry Pi OS):

bash
sudo apt update
sudo apt install -y python3-pip python3-venv libttspico-utils gpsd sox
libttspico-utils provides the pico2wave text-to-speech engine
sox is required — it's used to convert and trim every announcement before playback
gpsd is only needed if you plan to use GPS-based location (mobile/portable stations); it's harmless to install either way
2. Get the code

Choose whichever is easier for you:

Option A — git clone (if git is installed):

bash
cd /opt
sudo git clone https://github.com/swanie98635/ASL3_wx.git asl3_wx_announce
cd asl3_wx_announce

Option B — download the ZIP (no git required):

On GitHub, click the green Code button → Download ZIP
Transfer the ZIP to your Pi (e.g. via scp, or download directly on the Pi with wget)
Unzip it into /opt/asl3_wx_announce

Either way, you should end up with the project files at /opt/asl3_wx_announce.

3. Create a virtual environment and install dependencies
bash
cd /opt/asl3_wx_announce
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

A couple of the dependencies (numpy, reverse_geocoder) include compiled components. On Raspberry Pi OS, pip is usually already configured to pull pre-built packages from piwheels.org automatically, so this should still install in a few minutes rather than compiling from source. If it seems to hang for a long time, it's likely compiling — let it finish, or check that piwheels is configured.

4. Configure your station

Copy the example config and edit it with your own details:

bash
cp config.example.yaml config.yaml
nano config.yaml

The most important fields to change:

yaml
location:
  source: fixed        # or 'gpsd' if you're mobile and have a GPS attached
  latitude: 0.0000      # your station's latitude
  longitude: 0.0000     # your station's longitude
  timezone: "America/New_York"   # your local timezone

station:
  callsign: "MYCALL"    # your amateur radio callsign

voice:
  nodes:
    - "1000"            # your AllStarLink node number(s)

Everything else in the file has inline comments explaining what it does — alert severity thresholds, the alert tone, hourly report content, and so on.

5. Test it before relying on it

Run a one-off report to make sure everything's working end to end:

bash
python3 -m asl3_wx_announce.main --config config.yaml --report

You should hear your node announce a full weather report. If it fails, check the terminal output — it will usually point directly at the missing piece (a bad node number, missing pico2wave, etc.).

To test the alert tone and message sequence specifically:

bash
python3 -m asl3_wx_announce.main --config config.yaml --test-alert
6. Run it continuously

For ongoing operation, use monitor mode, which watches for new alerts and also handles any scheduled hourly reports you've turned on in config.yaml:

bash
python3 -m asl3_wx_announce.main --config config.yaml --monitor

To have it start automatically and stay running, install it as a systemd service:

bash
sudo cp asl3-wx.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now asl3-wx

By default, asl3-wx.service expects the project (and its virtual environment) to live at /opt/asl3_wx_announce. If you installed it somewhere else, edit the WorkingDirectory and ExecStart lines in asl3-wx.service before copying it.

Check that it's running with:

bash
sudo systemctl status asl3-wx
journalctl -u asl3-wx -f
Troubleshooting
No audio plays at all: confirm libttspico-utils and sox are both installed, and that the user running the service has permission to write to /usr/share/asterisk/sounds/en and /tmp/asl3_wx.
Works when run manually but not as a service (or vice versa): this is usually a file-permission mismatch — the systemd service runs as root by default, so temp files created while testing as your normal user can end up with the wrong ownership. Clear out /tmp/asl3_wx and try again.
GPS location never resolves: confirm gpsd is running (systemctl status gpsd) and actually has a fix; otherwise switch location.source to fixed and set coordinates manually.
Contributing

Pull requests are welcome — see the asl3_wx_announce/provider/ directory to add support for additional countries or weather data sources.

License

MIT License
