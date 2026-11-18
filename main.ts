// news-image-20261117 entry (Node 22, standard library only): the image is the
// entry.png beside this file, a front page drawn for Tuesday 17 November 2026
// by draw_poster.py (Python + PIL, deterministic), and the program copies it
// to /output/entry.png. Deterministic: same bytes every run.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from 'node:fs';
import { join } from 'node:path';

// The grader sets MAKEFUN_OUTPUT_DIR to /output; locally it defaults there too.
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
