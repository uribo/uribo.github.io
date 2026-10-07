// Post-render step (registered in _quarto.yml). Social cards (X, Facebook, Slack, ...)
// do not display SVG, but pages take their Open Graph / Twitter image from their
// `image`, which is an SVG illustration. Point those tags at the matching PNG card in
// assets/social/ (rendered from assets/social/axis-card.html) and add its size.
// Runs on Quarto's bundled Deno, so CI needs no extra toolchain. Fails the build if an
// SVG image would still be published or a card is missing.

const outDir = Deno.env.get("QUARTO_PROJECT_OUTPUT_DIR") ?? "_site";
const CARDS: Record<string, string> = {
  "axis-he": "axis-he.png",
  "axis-ei": "axis-ei.png",
  "axis-hi": "axis-hi.png",
  "neutral": "axis-neutral.png",
};
const IMAGE_TAG_RE = /<meta (property="og:image"|name="twitter:image") content="([^"]*)">/g;
const SVG_RE = /\/assets\/illustrations\/([\w-]+)\.svg$/;
const errors: string[] = [];

async function* htmlFiles(dir: string): AsyncGenerator<string> {
  for await (const entry of Deno.readDir(dir)) {
    const path = `${dir}/${entry.name}`;
    if (entry.isDirectory) yield* htmlFiles(path);
    else if (entry.name.endsWith(".html")) yield path;
  }
}

for (const card of Object.values(CARDS)) {
  try {
    await Deno.stat(`${outDir}/assets/social/${card}`);
  } catch {
    errors.push(`missing ${outDir}/assets/social/${card} (is assets/social/*.png in project resources?)`);
  }
}

for await (const file of htmlFiles(outDir)) {
  const html = await Deno.readTextFile(file);
  let rewritten = false;
  // Quarto emits no size tags for SVG images, so adding them here does not duplicate.
  const updated = html.replace(IMAGE_TAG_RE, (tag, attr, url) => {
    const match = url.match(SVG_RE);
    if (!match) return tag;
    const card = CARDS[match[1]];
    if (!card) {
      errors.push(`${file}: no PNG card for ${url}`);
      return tag;
    }
    rewritten = true;
    const pngUrl = url.replace(SVG_RE, `/assets/social/${card}`);
    const size = attr.startsWith("property")
      ? `\n<meta property="og:image:width" content="1280">\n<meta property="og:image:height" content="640">`
      : `\n<meta name="twitter:image-width" content="1280">\n<meta name="twitter:image-height" content="640">`;
    return `<meta ${attr} content="${pngUrl}">${size}`;
  });
  if (rewritten) await Deno.writeTextFile(file, updated);
  for (const [, , url] of updated.matchAll(IMAGE_TAG_RE)) {
    if (url.endsWith(".svg")) errors.push(`${file}: social image is still an SVG (${url})`);
  }
}

if (errors.length > 0) {
  for (const e of errors) console.error(`og-images: ${e}`);
  Deno.exit(1);
}
