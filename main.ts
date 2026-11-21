// THE WORLD TODAY - Saturday, 21 November 2026.
// Copies the pre-built newspaper image to the output directory.
// Deterministic: byte-identical on every run (plain file copy).
import { copyFileSync, mkdirSync } from "node:fs";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "out";
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL("./entry.png", import.meta.url), `${outDir}/entry.png`);
