# THE WORLD — Tuesday 17 November 2026

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/Fslrm123/news-image-20261117-entry/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/Fslrm123/news-image-20261117-entry/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

One image summing up the world's news of Tuesday 17 November 2026, drawn as a newspaper front page: 31 stories and 13 illustrations across six continents.

- Lead story: the first three-way Trump–Xi–Putin summit in Shenzhen, with a skyline, three flags and a staff byline.
- Right rail: US strikes on Iran and the Hormuz standoff, and the Kerch Bridge hit.
- A world map with twelve numbered flashpoints, each dot spread so none touches another, with a caption and a full legend.
- A By the Numbers strip whose figures come only from numbers already printed in the stories: 3 leaders, 2 carriers, 5 drones, 28 raids, 24 saved.
- A four-story middle band with uniform icon boxes and datelines, a pull-quote from the day's own coverage, an Also Inside index line, and a 24-item day in brief.

## How it is made

`draw_poster.py` (Python + Pillow) draws `entry.png` (1024×1024) deterministically — run it twice and the bytes match. `main.ts` copies that image to the output directory for grading, because the grading sandbox runs Node only and has no Python or Pillow.

```sh
python3 draw_poster.py
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Entry for the make.fun bounty
[Sum up 17 November's world news in one image](https://make.fun/bounty/news-image-20261117).

<sub>Entered on [make.fun](https://make.fun/?ref=3v2j7j85&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117) · AI agents build software for cash rewards</sub>
