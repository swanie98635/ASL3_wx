# ASL3 Weather Announcer (ASL3_wx)

**ASL3 Weather Announcer** is a Python-based weather and civil-alert announcer for [AllStarLink 3](https://www.allstarlink.org/) (Asterisk) amateur radio nodes. It periodically checks official weather sources and, when something is issued for your area, generates a spoken announcement and plays it out over your node — no internet radio, no cloud TTS, no GPU required.

This is the lightweight, fully offline-TTS version of the project — it's built to run comfortably on a Raspberry Pi (or similar single-board computer) alongside your existing AllStarLink node software. A separate, more resource-intensive companion project handles voice-cloned announcements for people who want a more natural-sounding voice and have a machine to spare for it; this repo is for everyone else.

It provides automated verbal announcements for:
- **Active weather alerts** — warnings, watches, and advisories, as they're issued
- **Scheduled reports** — forecast, current conditions, sunrise/sunset and moon phase, read out on a schedule you set
- **Time announcements** — spoken local time at the start of each report

## Features

- **[Multi-country support](https://github.com/swanie98635/ASL3_wx/blob/main/asl3_wx_announce/provider/factory.py#L34)**: National Weather Service (NWS) data for the US, Environment Canada data for Canada, with a plugin-style provider architecture so more countries can be added
- **Flexible location**: GPS via `gpsd` for mobile/portable stations, or a fixed lat/lon for a permanent install
- **English and French** announcements, with the groundwork in place for more languages
- **[Configurable alert tone](https://github.com/swanie98635/ASL3_wx/blob/main/config.example.yaml#L45-L47)**: an attention tone can play automatically ahead of Warning-level (or higher) alerts, generated and triggered [here](https://github.com/swanie98635/ASL3_wx/blob/main/asl3_wx_announce/main.py#L273-L291)
- **[Canada's Alert Ready system](https://github.com/swanie98635/ASL3_wx/blob/main/asl3_wx_announce/provider/alert_ready.py)**: optional support for non-weather civil emergency alerts, in addition to Environment Canada weather data
- **Offline TTS by default**: uses [`pico2wave`](https://github.com/swanie98635/ASL3_wx/blob/main/config.example.yaml#L29-L30), a small, fast, fully offline speech engine that runs comfortably on a Raspberry Pi

## Recommended hardware

This project is deliberately built to be easy for hams to run on hardware they probably already have.

- **A Raspberry Pi is the easiest path.** Because the text-to-speech engine (`pico2wave`) runs entirely offline with no GPU or significant CPU load, this doesn't need anything more powerful than a Raspberry Pi 3B+ or 4. A great many AllStarLink nodes already run on a Pi, so in most cases you can install this directly on the same Pi that's running your node — no extra hardware needed.
- **Minimum practical spec**: Raspberry Pi 3B+ or newer (a Pi 4 with 2GB+ RAM is a comfortable choice), a 16GB or larger SD card (Class 10 / A1 rated, or better yet a USB SSD for reliability), and a stable internet connection for polling weather data.
- **Other SBCs work fine too** — this is plain Python with a handful of pip packages, so an Orange Pi, NanoPi, Rock Pi, or an old laptop running Linux will all work equally well. The Raspberry Pi is just the most common and best-documented option in the ham community.
- If your AllStarLink node is already running close to its limits (busy with other add-ons, SDR monitoring, etc.), running this on a second, inexpensive Pi dedicated to just this task is a reasonable alternative.

## Legal note for US operators (FCC Part 97)

This project touches two distinct FCC exceptions to the general ban on one-way amateur transmissions, and it's worth understanding both — along with a real ambiguity in how well either one actually fits what this software does.

**Weather content — 47 CFR §97.113(c).** Part 97 generally bars amateur stations from retransmitting signals originating from a non-amateur station. §97.113(c) carves out an exception specifically for propagation and weather forecast information intended for the general public that originates from a United States Government source (NWS data qualifies). Two limits matter here:

- **It only covers U.S. Government-sourced data.** If you enable the Environment Canada provider, this FCC exception doesn't extend to that data — see the Canada note below.
- **It's for occasional use, not a standing schedule.** The rule's own text says such retransmissions "may not be conducted on a regular basis, but only occasionally, as an incident of normal amateur radio communications." A strict reading puts *routine, continuous scheduled reports* — this project's [`hourly_report` config](https://github.com/swanie98635/ASL3_wx/blob/main/config.example.yaml#L14-L26), checked every minute in [the monitor loop](https://github.com/swanie98635/ASL3_wx/blob/main/asl3_wx_announce/main.py#L189-L205) — in a genuine gray area. Alert-driven announcements — a [Watch, Warning, or Critical](https://github.com/swanie98635/ASL3_wx/blob/main/asl3_wx_announce/models.py#L6-L11) event, filtered by [`min_severity`](https://github.com/swanie98635/ASL3_wx/blob/main/config.example.yaml#L42) — sit on firmer ground under the separate safety-of-life/protection-of-property exception in §97.113(b), which carries no "occasional use" restriction.

**There's a further wrinkle worth being direct about**: §97.113(c) is written around *retransmission* — literally relaying "programs or signals emanating from" another station, the classic case being piping NOAA Weather Radio audio through in real time. This project doesn't do that. It fetches structured data from NWS/Environment Canada APIs and synthesizes new, original speech locally; no program or signal from another station is ever relayed. A strict textual reading could reasonably conclude that §97.113(c) doesn't even apply here one way or the other, since nothing is being "retransmitted" at all — which means the weather-report feature may rest more on the information-bulletin exception below (or the alert-driven safety exception) than on the weather-specific carve-out itself. This is a genuine, unresolved gray area, not a settled question — it doesn't cut cleanly toward "definitely fine" or "definitely not."

**Propagation bulletins — 47 CFR §97.111(b)(6).** Separately, this provision authorizes one-way transmissions to "disseminate information bulletins." It doesn't define what counts as a bulletin, but propagation data — solar flux index, K-index, and similar space-weather reports — is the long-standing, textbook example (the same basis ARRL's W1AW propagation bulletins run on). This provision doesn't require retransmission of anything, and it carries no "occasional, not regular" restriction, so the [`solar_flux` report content](https://github.com/swanie98635/ASL3_wx/blob/main/config.example.yaml#L24) — [generated here](https://github.com/swanie98635/ASL3_wx/blob/main/asl3_wx_announce/narrator.py#L287-L294) — sits on considerably firmer ground than the weather-forecast content does — and by the same logic, could be the more defensible basis for the weather content too, if you read "weather report bulletin" as a kind of information bulletin rather than as a retransmission.

**Weather isn't just a general-public convenience for hams — it's operationally relevant to the amateur radio service itself.** This matters for the information-bulletin argument above, since it helps support that weather content is of direct interest to amateur operators, not only to the general public. Weather has a real, direct bearing on radio operation in at least two ways: tropospheric conditions (temperature inversions, humidity, pressure gradients) affect VHF/UHF propagation and ducting, and ionospheric disturbances tied to space weather affect HF propagation — both squarely within amateur radio's own technical concerns. Separately, advance warning of approaching thunderstorms gives an operator time to disconnect antennas and protect sensitive equipment from lightning-induced surges, which is a standard, well-known station-safety practice. The [severe thunderstorm and tornado warnings](https://github.com/swanie98635/ASL3_wx/blob/main/config.example.yaml#L60-L72) this project already surfaces through the [standard alert feed](https://github.com/swanie98635/ASL3_wx/blob/main/asl3_wx_announce/narrator.py#L112) serve that purpose directly, independent of the general civil-safety rationale.

## Legal note for Canadian operators

Canada does not have a direct equivalent to either FCC provision above. I looked through RIC-3 (Information on the Amateur Radio Service), RBR-4 (Standards for the Operation of Radio Stations in the Amateur Radio Service), and the Radiocommunication Regulations (SOR/96-484) directly: none of them contain a codified exception for retransmitting or disseminating weather or propagation information the way §97.113(c) and §97.111(b)(6) do in the US. Canada previously had a general content restriction (the former section 32, requiring transmissions to be "non-superfluous" and free of profanity), but it was repealed in 2011 without anything specific put in its place. The Basic certification exam still tests that amateur stations generally shouldn't retransmit non-amateur programming, but there's no equivalent explicit carve-out on the books for weather or propagation bulletins specifically.

Practically, this means enabling the Environment Canada provider or the [Alert Ready feature](https://github.com/swanie98635/ASL3_wx/blob/main/config.example.yaml#L57) rests on less defined ground in Canada than the equivalent US features do — not because it's clearly prohibited, but because there's no specific rule spelling out that it's permitted, one way or the other. If you're a VE/VA operator planning to run this regularly, it's worth reaching out to Radio Amateurs of Canada (RAC) or your local club directly, since this is exactly the kind of question ISED-facing organizations like RAC are positioned to answer, and I wasn't able to find a clear, current, codified answer either way.

## Make your Own Legal Decision Before Using

This isn't legal advice, and I'm not an attorney — you're responsible for how you configure and operate your own station under your own license. If you're planning to run frequent scheduled weather reports (rather than alert-driven weather announcements only), it's worth reading the full text of 47 CFR §97.111 and §97.113 yourself (US) or the current Radiocommunication Regulations (Canada) and, if you have any doubt, checking with your section's ARRL Volunteer Counsel, Radio Amateurs of Canada (RAC), or your club's technical resources before deploying this on a live repeater.

## Installation

This guide assumes basic comfort with the Linux command line (typing commands over SSH) but no prior Python experience.

### 1. Install system prerequisites

On your ASL3 server (Debian/Raspberry Pi OS):

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv libttspico-utils gpsd sox
```

- `libttspico-utils` provides the `pico2wave` text-to-speech engine
- `sox` is required — it's used to convert and trim every announcement before playback
- `gpsd` is only needed if you plan to use GPS-based location (mobile/portable stations); it's harmless to install either way

### 2. Get the code

Choose whichever is easier for you:

**Option A — git clone** (if git is installed):
```bash
cd /opt
sudo git clone https://github.com/swanie98635/ASL3_wx.git asl3_wx_announce
cd asl3_wx_announce
```

**Option B — download the ZIP** (no git required):
1. On GitHub, click the green **Code** button → **Download ZIP**
2. Transfer the ZIP to your Pi (e.g. via `scp`, or download directly on the Pi with `wget`)
3. Unzip it into `/opt/asl3_wx_announce`

Either way, you should end up with the project files at `/opt/asl3_wx_announce`.

### 3. Create a virtual environment and install dependencies

```bash
cd /opt/asl3_wx_announce
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

A couple of the dependencies (`numpy`, `reverse_geocoder`) include compiled components. On Raspberry Pi OS, pip is usually already configured to pull pre-built packages from [piwheels.org](https://www.piwheels.org/) automatically, so this should still install in a few minutes rather than compiling from source. If it seems to hang for a long time, it's likely compiling — let it finish, or check that piwheels is configured.

### 4. Configure your station

Copy the [example config](https://github.com/swanie98635/ASL3_wx/blob/main/config.example.yaml) and edit it with your own details:

```bash
cp config.example.yaml config.yaml
nano config.yaml
```

The most important fields to change:

```yaml
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
```

Everything else in the file has inline comments explaining what it does — alert severity thresholds, the alert tone, hourly report content, and so on.

### 5. Test it before relying on it

Run a one-off report to make sure everything's working end to end:

```bash
python3 -m asl3_wx_announce.main --config config.yaml --report
```

You should hear your node announce a full weather report. If it fails, check the terminal output — it will usually point directly at the missing piece (a bad node number, missing `pico2wave`, etc.).

To test the alert tone and message sequence specifically:

```bash
python3 -m asl3_wx_announce.main --config config.yaml --test-alert
```

### 6. Run it continuously

For ongoing operation, use [monitor mode](https://github.com/swanie98635/ASL3_wx/blob/main/asl3_wx_announce/main.py#L113), which watches for new alerts and also handles any scheduled hourly reports you've turned on in `config.yaml`:

```bash
python3 -m asl3_wx_announce.main --config config.yaml --monitor
```

To have it start automatically and stay running, install it as a [systemd service](https://github.com/swanie98635/ASL3_wx/blob/main/asl3-wx.service):

```bash
sudo cp asl3-wx.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now asl3-wx
```

By default, `asl3-wx.service` expects the project (and its virtual environment) to live at `/opt/asl3_wx_announce`. If you installed it somewhere else, edit the `WorkingDirectory` and `ExecStart` lines in `asl3-wx.service` before copying it.

Check that it's running with:

```bash
sudo systemctl status asl3-wx
journalctl -u asl3-wx -f
```

## Troubleshooting

- **No audio plays at all**: confirm `libttspico-utils` and `sox` are both installed, and that the user running the service has permission to write to `/usr/share/asterisk/sounds/en` and `/tmp/asl3_wx`.
- **Works when run manually but not as a service (or vice versa)**: this is usually a file-permission mismatch — the systemd service runs as `root` by default, so temp files created while testing as your normal user can end up with the wrong ownership. Clear out `/tmp/asl3_wx` and try again.
- **GPS location never resolves**: confirm `gpsd` is running (`systemctl status gpsd`) and actually has a fix; otherwise switch `location.source` to `fixed` and set coordinates manually.

## Contributing

Pull requests are welcome — see the [`asl3_wx_announce/provider/`](https://github.com/swanie98635/ASL3_wx/tree/main/asl3_wx_announce/provider) directory to add support for additional countries or weather data sources.

## License

MIT License
