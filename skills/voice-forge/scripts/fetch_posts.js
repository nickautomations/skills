#!/usr/bin/env node
/*
 * fetch_posts.js — Scrape a LinkedIn creator's posts via the Apify actor
 *   capable_cauldron/linkedin-profile-posts-scraper
 *
 * Uses only Node.js built-ins (fetch, fs). No npm install required.
 *
 * Usage:
 *   node fetch_posts.js --username <linkedinUsernameOrUrl> --max 100 --out data/<username>/raw_posts.json
 *
 * Requires APIFY_API_TOKEN, read from the environment or from scripts/.env
 * beside this file. The token is NEVER accepted as a CLI argument, NEVER
 * logged, and NEVER written to the output — an argument would leak it into
 * shell history and process listings.
 *
 * Resume logic: if --out already exists, the script exits 0 with a notice
 * instead of re-scraping (and re-charging Apify).
 */

const fs = require("fs");
const path = require("path");

// --- Actor identifier ---------------------------------------------------
const ACTOR_ID = "capable_cauldron~linkedin-profile-posts-scraper";
const API_BASE = "https://api.apify.com/v2";

// --- Credentials ---------------------------------------------------------
// Read scripts/.env beside this file, so the token is found no matter which
// directory the script is invoked from. A real environment variable wins, so
// setting APIFY_API_TOKEN in the shell always overrides the file.
const ENV_PATH = path.join(__dirname, ".env");

function loadEnvFile() {
  const envPath = ENV_PATH;
  if (!fs.existsSync(envPath)) return;

  for (const line of fs.readFileSync(envPath, "utf8").split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;

    const eq = trimmed.indexOf("=");
    if (eq === -1) continue;

    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if (value.length >= 2 && value[0] === value[value.length - 1] && (value[0] === '"' || value[0] === "'")) {
      value = value.slice(1, -1);
    }
    if (key && process.env[key] === undefined) process.env[key] = value;
  }
}

// --- Argument parsing ---------------------------------------------------
function parseArgs(argv) {
  // `out` defaults to data/<username>/raw_posts.json once the username is known,
  // so two creators never share a cache file (and never resume off each other).
  const args = { username: null, max: 100, out: null };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--username" || a === "-u") args.username = argv[++i];
    else if (a === "--max" || a === "-m") args.max = parseInt(argv[++i], 10);
    else if (a === "--out" || a === "-o") args.out = argv[++i];
    else if (a === "--force") args.force = true;
    else if (a === "--help" || a === "-h") {
      console.log(
        "Usage: node fetch_posts.js --username <url|username> [--max 100] " +
          "[--out data/<username>/raw_posts.json] [--force]"
      );
      process.exit(0);
    }
  }
  return args;
}

// Pull the username out of a full LinkedIn URL if the user pasted one.
function normalizeUsername(input) {
  if (!input) return null;
  const trimmed = input.trim();
  // linkedin.com/in/<username>/...
  const m = trimmed.match(/linkedin\.com\/in\/([^/?#\s]+)/i);
  if (m) return decodeURIComponent(m[1]);
  // Already a bare username
  return trimmed;
}

// Make a username safe to use as a single path segment.
function slugForPath(username) {
  const slug = username.toLowerCase().replace(/[^a-z0-9._-]+/g, "-").replace(/^-+|-+$/g, "");
  return slug || "profile";
}

// --- Apify HTTP helpers -------------------------------------------------
async function startRun(token, username, maxPosts) {
  const body = {
    usernames: [username],
    maxPostsPerProfile: maxPosts,
    maxDatasetItems: maxPosts, // hard cap = post limit, so cost can't overrun
  };
  const url = `${API_BASE}/acts/${ACTOR_ID}/runs?token=${encodeURIComponent(token)}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Apify start-run failed (${res.status}): ${text}`);
  }
  const run = await res.json();
  return run.data;
}

async function pollRun(token, runId) {
  const url = `${API_BASE}/actor-runs/${runId}?token=${encodeURIComponent(token)}`;
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Apify poll failed (${res.status}): ${text}`);
  }
  const run = await res.json();
  return run.data;
}

async function getDatasetItems(token, defaultDatasetId) {
  // Paginate defensively — 100 posts fit in one page, but keep the loop.
  const all = [];
  let offset = 0;
  const limit = 1000;
  while (true) {
    const url =
      `${API_BASE}/datasets/${defaultDatasetId}/items` +
      `?token=${encodeURIComponent(token)}&offset=${offset}&limit=${limit}`;
    const res = await fetch(url);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Apify dataset fetch failed (${res.status}): ${text}`);
    }
    const page = await res.json();
    if (!Array.isArray(page) || page.length === 0) break;
    all.push(...page);
    if (page.length < limit) break;
    offset += limit;
  }
  return all;
}

// --- Main ----------------------------------------------------------------
async function main() {
  const args = parseArgs(process.argv);

  if (!args.username) {
    console.error("Error: --username is required.");
    process.exit(2);
  }

  const username = normalizeUsername(args.username);

  // Resume logic: skip if output exists and --force not set.
  const outPath = path.resolve(
    args.out || path.join("data", slugForPath(username), "raw_posts.json")
  );
  if (!args.force && fs.existsSync(outPath)) {
    const existing = JSON.parse(fs.readFileSync(outPath, "utf8"));
    console.log(
      `SKIP: ${outPath} already exists with ${existing.length} posts. Use --force to re-scrape.`
    );
    return;
  }

  loadEnvFile();
  const token = process.env.APIFY_API_TOKEN;
  if (!token) {
    console.error(
      "Error: APIFY_API_TOKEN is not set.\n" +
        "Get a token at https://console.apify.com/account/integrations, then do either:\n" +
        `  - put this line in ${ENV_PATH}\n` +
        "        APIFY_API_TOKEN=your_token_here\n" +
        "  - or set APIFY_API_TOKEN in your environment and restart Claude Code."
    );
    process.exit(3);
  }

  const max = args.max || 100;
  console.log(`Scraping up to ${max} posts for "${username}" ...`);

  // Start
  const start = await startRun(token, username, max);
  const runId = start.id;
  const datasetId = start.defaultDatasetId;
  console.log(`Run started: ${runId}`);

  // Poll every 5s
  const startedAt = Date.now();
  let status = start.status;
  while (
    status === "RUNNING" ||
    status === "READY" ||
    status === "STARTING"
  ) {
    await new Promise((r) => setTimeout(r, 5000));
    const latest = await pollRun(token, runId);
    status = latest.status;
    const elapsed = Math.round((Date.now() - startedAt) / 1000);
    process.stdout.write(`\rStatus: ${status} (${elapsed}s)   `);
    if (status === "SUCCEEDED") break;
    if (status === "FAILED" || status === "ABORTED" || status === "TIMED-OUT") {
      console.error("");
      console.error(`Run ended with status: ${status}`);
      process.exit(4);
    }
  }
  console.log("\nRun finished. Fetching dataset ...");

  // Dataset
  const items = await getDatasetItems(token, datasetId);
  console.log(`Got ${items.length} raw posts.`);

  // Persist
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(items, null, 2), "utf8");
  console.log(`Wrote ${items.length} posts -> ${outPath}`);
}

main().catch((err) => {
  console.error("Fatal:", err.message);
  process.exit(1);
});
