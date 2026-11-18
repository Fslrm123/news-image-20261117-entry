// Entry point for the news-image-20261117 bounty.
//
// The poster is drawn by draw_poster.py and committed as entry.png.
// This program copies it to the output directory the grader gives us
// (MAKEFUN_OUTPUT_DIR), so the run needs no network and no extra
// packages: the image it writes is byte for byte the one in the repo.
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const outDir = process.env.MAKEFUN_OUTPUT_DIR || "out";
mkdirSync(outDir, { recursive: true });

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
if (!existsSync(src)) {
  throw new Error("entry.png is missing next to main.ts");
}
const dest = join(outDir, "entry.png");
copyFileSync(src, dest);
console.log("wrote", dest);
