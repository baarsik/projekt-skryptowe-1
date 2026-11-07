import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

// Check the deployable artifact, not .next's server output. Run after next build.
const out = fileURLToPath(new URL("../../frontend/out/", import.meta.url));
const pages = [
  { route: "", links: ["login"], en: "Welcome", pl: "Witaj" },
  {
    route: "login",
    links: ["signup", "forgot-password"],
    en: "Welcome back",
    pl: "Witaj ponownie",
  },
  {
    route: "signup",
    links: ["login"],
    en: "Create an account",
    pl: "Utwórz konto",
  },
  {
    route: "forgot-password",
    links: ["login"],
    en: "Forgot your password?",
    pl: "Nie pamiętasz hasła?",
  },
];

async function readExport(relative) {
  const content = await readFile(join(out, relative), "utf8");
  assert.ok(content.trim(), `Empty exported file: ${relative}`);
  return content;
}

for (const locale of ["en", "pl"]) {
  for (const page of pages) {
    const relative = join(locale, page.route, "index.html");
    const html = await readExport(relative);
    // Ignore React's serialized payload: assertions must inspect rendered HTML.
    const markup = html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, "");
    assert.match(
      markup,
      new RegExp(`<html\\b[^>]*\\blang="${locale}"`),
      relative,
    );
    const heading = page[locale].replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    assert.match(markup, new RegExp(`<h1\\b[^>]*>${heading}</h1>`), relative);
    for (const link of page.links) {
      assert.ok(
        markup.includes(`href="/${locale}/${link}/"`),
        `${relative}: missing localized link to ${link}`,
      );
    }
    const assets = [...html.matchAll(/(?:src|href)="(\/_next\/[^"?]+\.(?:js|css))(?:\?[^"\s]*)?"/g)];
    for (const extension of [".js", ".css"]) {
      assert.ok(
        assets.some(([, asset]) => asset.endsWith(extension)),
        `${relative}: missing ${extension} assets`,
      );
    }
    for (const [, asset] of assets) {
      await readExport(asset.slice(1));
    }
  }
}

const root = await readExport("index.html");
assert.match(
  root,
  /<meta\b[^>]*http-equiv="refresh"[^>]*content="0;url=\/pl\/"/i,
  "Root must redirect to /pl/ without middleware",
);
const notFound = await readExport("404.html");
assert.doesNotMatch(notFound, /http-equiv="refresh"/i, "404 must not redirect to the home page");
console.log("Static export verified: eight localized pages, links, assets, root redirect and 404.");
