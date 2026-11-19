# World in Brief · 19 November 2026

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/rozikin45/world-in-brief-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/rozikin45/world-in-brief-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

**An original, evidence-checked early edition — as of 04:00 UTC.** Six developments, one square image. This is a morning snapshot, not a claim that all of 19 November has finished.

![World in Brief: 19 November 2026, early edition](entry.png)

## Run it

The competition entrypoint uses **Python 3.13 and its standard library only**:

```sh
python3.13 main.py
```

It validates the committed artwork and writes exactly `/output/entry.png`. For a local folder that does not require access to `/output`:

```sh
python3.13 -I -S main.py --output-dir ./out
```

The runner deliberately emits the exact bytes of the original, bundled `entry.png`. It does not browse the news again, fetch fonts, call an image model, contact a network service, need an API key, or depend on Pillow at runtime. The artwork is fixed to the edition and cutoff printed on it.

## What made the edition

- **Diplomacy:** Trump, Xi and Putin in the APEC leaders' group photo, Shenzhen — not an asserted trilateral agreement.[4][15]
- **Russia–Ukraine:** a Crimean Bridge closure attributed to the Russian-installed governor — not a claim about new damage or the current reopening state.[8][18]
- **Weather:** Cyclone Akvan tracked toward India's coast; 20 November landfall clearly remains a forecast.[28][30]
- **Economic data:** Australia's **October** seasonally adjusted unemployment rate, **4.9%**, released on 19 November.[27][25]
- **Culture:** GTA VI's digital launch begins **region by region**, not all markets simultaneously.[33][34]
- **Earthquake:** a new Kumamoto tremor at **02:22 JST**, **preliminary M5.7**, without an unverified casualty claim.[23][20]

[Reporting, publication times, date eligibility, caveats and source links](SOURCES.md) · [Structured story data](news.json)

## Verify the runtime

```sh
python3.13 -m unittest -v test_main
```

The tests execute two isolated runs with third-party site packages disabled, compare output bytes, check the PNG dimensions and byte cap, and require corrupted PNG chunk data to be rejected before output. The runnable entrypoint is `main.py`; `render.py` is an optional development tool, not the competition runtime.

## Rebuild the original artwork

For maintainers who want to edit the design, install the development-only image library:

```sh
python3 -m pip install Pillow==11.1.0
python3 render.py
```

The bundled Noto font files make the design source portable. The renderer writes `entry.png`, a real `preview-300.png` downscale, and `design/layout-audit.json` with text bounding boxes and the image digest. `design/analysis.md` explains the composition and verification decisions. Full news articles and private agent logs are not part of the public repository.

## Originality and licenses

The geometric illustrations are original symbolic line art: a group-photo viewfinder, an intact bridge with a stop marker, a cyclone mark and a generic gamepad. They are not altered wire photographs, documentary imagery, game screenshots or copied promotional character art.

Original code, editorial text and artwork: **MIT**. Noto fonts remain **SIL Open Font License 1.1**; copyright and license terms are bundled in `fonts/NOTO-LICENSE.txt`. News facts are attributed to their sources; this repository does not republish the articles.

---

<sub>Entered on [make.fun](https://make.fun/?ref=xv1e6sta&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards. The link includes the account's referral code; no reward is promised to a reader.</sub>

## Sources

[4] https://www.gmanetwork.com/news/topstories/world/1010030/trump-says-historic-summit-with-xi-putin-already-a-win-before-event/story
[8] https://www.arabnews.com/world/third-attack-in-a-week-suspends-traffic-over-crimean-bridge-russian-official-says-3012816
[15] https://www.cnbc.com/video/2026/11/19/trump-xi-putin-and-other-world-leaders-arrive-for-apec-summit.html
[18] https://kyivindependent.com/ukrainian-forces-once-more-hit-russias-crimean-bridge-days-after-devastating-strike
[20] https://www.nippon.com/en/articles/-/57685
[23] https://www.jma.go.jp/jma/press/2611/19a/202611190425.html
[25] https://www.abc.net.au/news/2026-11-19/unemployment-rate-jumps-in-october-in-australia/107399076
[27] https://www.abs.gov.au/media-centre/media-releases/unemployment-rate-rises-49
[28] https://mausam.imd.gov.in/backend/assets/cyclone_pdf/28__National_Bulletin_No_28-19Nov2026_0230IST.pdf
[30] https://cnbctv18.com/india/cyclone-akvan-update-andhra-and-odisha-to-face-heavy-rain-ahead-of-landfall-on-friday-20036940.htm
[33] https://www.1news.co.nz/2026/11/19/grand-theft-auto-vi-arrives-with-enormous-hype-and-expectations
[34] https://www.hindustantimes.com/india-news/gaming-colossus-makes-long-awaited-return-101795048655227.html
