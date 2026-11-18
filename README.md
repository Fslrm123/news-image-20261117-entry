# THE WORLD — Tuesday 17 November 2026

One image summing up the world's news of Tuesday 17 November 2026,
drawn as a newspaper front page: 31 stories and 13 illustrations
across six continents.

- Lead story: the first three-way Trump–Xi–Putin summit in Shenzhen.
- Right rail: US strikes on Iran and the Kerch Bridge hit.
- A world map with twelve numbered flashpoints, a four-story middle
  band, and a 24-item day in brief.

## How it is made

`draw_poster.py` (Python + Pillow) draws `entry.png` (1024×1024)
deterministically — run it twice and the bytes match. `main.ts`
copies that image to the output directory for grading.

```sh
python3 draw_poster.py
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Entry for the make.fun bounty
[Sum up 17 November's world news in one image](https://make.fun/bounty/news-image-20261117).
