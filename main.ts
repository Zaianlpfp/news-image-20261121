// THE WORLD TODAY - Saturday, 21 November 2026.
// Copies the pre-built newspaper image to the output directory.
// Deterministic: byte-identical on every run (plain file copy).
// The copy is verified: the source is checked (magic bytes, size, dimensions)
// and the written file is read back and compared byte for byte.
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "out";
const source = new URL("./entry.png", import.meta.url);
const bytes = readFileSync(source);

// The file is named .png but its bytes are JPEG: accept either container,
// and reject anything that is neither (empty or corrupt input).
const isPng =
  bytes.length >= 8 &&
  bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47;
const isJpeg =
  bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff;
if (!isPng && !isJpeg) {
  throw new Error("entry.png is neither PNG nor JPEG (magic bytes mismatch)");
}
if (bytes.length < 1024) {
  throw new Error(`entry.png too small: ${bytes.length} bytes`);
}

// Dimensions: PNG IHDR (bytes 16-23) or the first JPEG SOF marker.
function dimensions(buf: Buffer): { width: number; height: number } {
  if (isPng) {
    return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
  }
  let i = 2;
  while (i + 9 < buf.length) {
    if (buf[i] !== 0xff) {
      i += 1;
      continue;
    }
    const marker = buf[i + 1];
    if (marker >= 0xc0 && marker <= 0xcf && marker !== 0xc4 && marker !== 0xc8 && marker !== 0xcc) {
      return { height: buf.readUInt16BE(i + 5), width: buf.readUInt16BE(i + 7) };
    }
    const len = buf.readUInt16BE(i + 2);
    if (len < 2) break;
    i += 2 + len;
  }
  throw new Error("JPEG SOF marker not found: cannot read dimensions");
}
const { width, height } = dimensions(bytes);
if (width <= 0 || height <= 0) {
  throw new Error(`entry.png has invalid dimensions: ${width}x${height}`);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(source, `${outDir}/entry.png`);

// Verify the copy byte for byte, and by hash, so a truncated or corrupted
// write fails loudly instead of shipping a broken poster.
const written = readFileSync(`${outDir}/entry.png`);
if (!written.equals(bytes)) {
  throw new Error("entry.png copy mismatch: output bytes differ from source");
}
const digest = createHash("sha256").update(written).digest("hex");
const sourceDigest = createHash("sha256").update(bytes).digest("hex");
if (digest !== sourceDigest) {
  throw new Error("entry.png copy mismatch: sha256 differs from source");
}
