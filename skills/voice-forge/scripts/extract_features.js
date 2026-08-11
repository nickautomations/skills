#!/usr/bin/env node
/*
 * extract_features.js — Turn raw scraped posts into a deterministic feature digest.
 *
 * This script does EVERYTHING measurable so the LLM never has to count, sum,
 * average, or rank anything. The output features.json is the only artifact the
 * voice-analysis LLM reads.
 *
 * It replaces what would otherwise be a "cleaning" stage. The source actor
 * (capable_cauldron/linkedin-profile-posts-scraper) already pre-enriches 55
 * fields, so we only SELECT the 14 we need and DEDUPLICATE — never transform.
 *
 * Usage:
 *   node extract_features.js --in data/<username>/raw_posts.json --out data/<username>/features.json
 *
 * Resume logic: if --out already exists, exits 0 with a notice.
 */

const fs = require("fs");
const path = require("path");

// The only fields the downstream analysis needs. Everything else is dropped.
const SELECT_FIELDS = [
  "text",
  "posted_date_iso",
  "content_category",
  "media_type",
  "total_engagement",
  "reaction_like",
  "reaction_love",
  "reaction_celebrate",
  "reaction_insight",
  "num_comments",
  "word_count",
  "is_repost",
  "share_urn",
  "post_url",
];

// --- Argument parsing ---------------------------------------------------
function parseArgs(argv) {
  // `out` defaults to features.json beside the input, keeping each creator's
  // artifacts together in their own data/<username>/ folder.
  const args = { in: "data/raw_posts.json", out: null };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--in" || a === "-i") args.in = argv[++i];
    else if (a === "--out" || a === "-o") args.out = argv[++i];
    else if (a === "--force") args.force = true;
  }
  return args;
}

// --- Stats helpers (all deterministic) ----------------------------------
function num(v) {
  const n = typeof v === "number" ? v : parseFloat(v);
  return Number.isFinite(n) ? n : 0;
}

function quantile(sorted, q) {
  // q in [0,1], sorted is ascending array of numbers.
  if (sorted.length === 0) return 0;
  const pos = (sorted.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  if (sorted[base + 1] !== undefined) {
    return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
  }
  return sorted[base];
}

function round(v, d = 2) {
  const m = Math.pow(10, d);
  return Math.round(v * m) / m;
}

function median(arr) {
  return quantile(arr.slice().sort((a, b) => a - b), 0.5);
}

// --- Selection + dedup --------------------------------------------------
function selectAndDedup(raw) {
  const seen = new Map(); // share_urn -> index
  const out = [];
  for (const r of raw) {
    // Drop reposts entirely — they're not the creator's voice.
    if (r.is_repost) continue;
    // Drop posts with no text (pure media with no caption is voice-less).
    if (!r.text || !r.text.trim()) continue;

    // Dedup key: share_urn preferred, fall back to text hash.
    const key = r.share_urn ? `urn:${r.share_urn}` : `txt:${r.text.trim()}`;
    if (seen.has(key)) continue;
    seen.set(key, true);

    const picked = {};
    for (const f of SELECT_FIELDS) picked[f] = r[f] ?? null;
    out.push(picked);
  }
  return out;
}

// --- Feature computation ------------------------------------------------
function buildFeatures(posts) {
  const n = posts.length;
  const engagements = posts.map((p) => num(p.total_engagement));
  const words = posts.map((p) => num(p.word_count) || (p.text ? p.text.split(/\s+/).filter(Boolean).length : 0));
  const comments = posts.map((p) => num(p.num_comments));
  const sortedEng = engagements.slice().sort((a, b) => a - b);

  // Format distribution
  const fmt = {};
  for (const p of posts) {
    const cat = p.content_category || p.media_type || "unknown";
    fmt[cat] = (fmt[cat] || 0) + 1;
  }

  // Reaction mix totals
  const reactionTotals = {
    like: 0,
    love: 0,
    celebrate: 0,
    insight: 0,
  };
  for (const p of posts) {
    reactionTotals.like += num(p.reaction_like);
    reactionTotals.love += num(p.reaction_love);
    reactionTotals.celebrate += num(p.reaction_celebrate);
    reactionTotals.insight += num(p.reaction_insight);
  }

  // Cadence: posts per weekday + per hour (UTC), from posted_date_iso
  const weekdayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const weekday = new Array(7).fill(0);
  const hour = new Array(24).fill(0);
  for (const p of posts) {
    if (!p.posted_date_iso) continue;
    const d = new Date(p.posted_date_iso);
    if (isNaN(d.getTime())) continue;
    weekday[d.getUTCDay()]++;
    hour[d.getUTCHours()]++;
  }
  const bestWeekday = weekdayNames[weekday.indexOf(Math.max(...weekday))];
  const bestHour = hour.indexOf(Math.max(...hour));

  // Outlier threshold: 2.5x median engagement (report the multiple used)
  const baseline = median(sortedEng) || 0;
  const outlierMultiple = 2.5;
  const outlierThreshold = baseline * outlierMultiple;

  // Top-30 by-engagement: full text + url, so the LLM can quote real lines.
  const topPosts = posts
    .slice()
    .sort((a, b) => num(b.total_engagement) - num(a.total_engagement))
    .slice(0, Math.min(30, n))
    .map((p, i) => ({
      rank: i + 1,
      text: p.text,
      url: p.post_url,
      engagement: num(p.total_engagement),
      comments: num(p.num_comments),
      word_count: num(p.word_count),
      format: p.content_category || p.media_type || "unknown",
      // Provide the first 2 lines (the hook) and last 2 lines (the close)
      // already split out — the LLM reads these to find opening/closing patterns.
      first_two_lines: (p.text || "").split(/\n/).filter((l) => l.trim()).slice(0, 2),
      last_two_lines: (p.text || "").split(/\n/).filter((l) => l.trim()).slice(-2),
    }));

  // Stratified sample: 20 posts spanning the engagement range (not just winners),
  // so the voice analysis sees the *middle* and *bottom* too.
  const sampled = [];
  if (n > 0) {
    const sortedAll = posts
      .slice()
      .sort((a, b) => num(a.total_engagement) - num(b.total_engagement));
    const sampleSize = Math.min(20, n);
    const step = Math.max(1, Math.floor(n / sampleSize));
    for (let i = 0; i < n && sampled.length < sampleSize; i += step) {
      const p = sortedAll[i];
      sampled.push({
        percentile_rank: Math.round((i / Math.max(1, n - 1)) * 100),
        text: p.text,
        url: p.post_url,
        engagement: num(p.total_engagement),
      });
    }
  }

  // Vocabulary tells (cheap structural signals, NOT a word list)
  let emojiCount = 0,
    questionCount = 0,
    exclamCount = 0,
    hashtagCount = 0;
  for (const p of posts) {
    const t = p.text || "";
    // Broad emoji match (pictographics + a few symbol blocks)
    const emojiMatches = t.match(
      /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2190}-\u{21FF}\u{2B00}-\u{2BFF}]/gu
    );
    if (emojiMatches) emojiCount += emojiMatches.length;
    questionCount += (t.match(/\?/g) || []).length;
    exclamCount += (t.match(/!/g) || []).length;
    hashtagCount += (t.match(/#/g) || []).length;
  }

  return {
    meta: {
      total_posts: n,
      generated_at: new Date().toISOString(),
      source_actor: "capable_cauldron/linkedin-profile-posts-scraper",
      outlier_multiple_used: outlierMultiple,
      fields_selected: SELECT_FIELDS,
    },
    volume_check: {
      posts: n,
      meets_floor: n >= 80, // voice-forge warns below this
    },
    engagement: {
      min: sortedEng[0] || 0,
      p25: round(quantile(sortedEng, 0.25)),
      median: round(quantile(sortedEng, 0.5)),
      p75: round(quantile(sortedEng, 0.75)),
      p90: round(quantile(sortedEng, 0.9)),
      max: sortedEng[n - 1] || 0,
      mean: round(engagements.reduce((a, b) => a + b, 0) / Math.max(1, n)),
      outlier_threshold: round(outlierThreshold),
      baseline_median: round(baseline),
    },
    length: {
      median_words: round(median(words)),
      mean_words: round(words.reduce((a, b) => a + b, 0) / Math.max(1, n)),
      min_words: Math.min(...words),
      max_words: Math.max(...words),
    },
    conversation: {
      median_comments: round(median(comments)),
      mean_comments: round(comments.reduce((a, b) => a + b, 0) / Math.max(1, n)),
      comment_to_engagement_ratio: round(
        comments.reduce((a, b) => a + b, 0) /
          Math.max(1, engagements.reduce((a, b) => a + b, 0))
      ),
    },
    format_distribution: fmt,
    reaction_mix: reactionTotals,
    cadence: {
      posts_per_weekday: weekdayNames.reduce((o, name, i) => {
        o[name] = weekday[i];
        return o;
      }, {}),
      best_weekday: bestWeekday,
      posts_per_hour_utc: hour,
      best_hour_utc: bestHour,
    },
    structural_signals: {
      total_emojis: emojiCount,
      emojis_per_post: round(emojiCount / Math.max(1, n)),
      questions_per_post: round(questionCount / Math.max(1, n)),
      exclamations_per_post: round(exclamCount / Math.max(1, n)),
      hashtags_per_post: round(hashtagCount / Math.max(1, n)),
      posts_with_emoji_pct: round(
        (posts.filter((p) =>
          /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/u.test(p.text || "")
        ).length /
          Math.max(1, n)) * 100
      ),
    },
    top_30_posts: topPosts,
    stratified_sample_20: sampled,
    // NOTE FOR THE LLM: every number above is exact and computed over ALL posts.
    // The top_30 and stratified_sample arrays are the ONLY raw text you need to read.
    // Do NOT recompute any number. Reason about WHY, using these as evidence.
  };
}

// --- Main ----------------------------------------------------------------
async function main() {
  const args = parseArgs(process.argv);
  const inPath = path.resolve(args.in);
  const outPath = path.resolve(args.out || path.join(path.dirname(inPath), "features.json"));

  if (!args.force && fs.existsSync(outPath)) {
    console.log(`SKIP: ${outPath} already exists. Use --force to re-extract.`);
    return;
  }

  if (!fs.existsSync(inPath)) {
    console.error(`Error: input not found: ${inPath}`);
    process.exit(2);
  }

  const raw = JSON.parse(fs.readFileSync(inPath, "utf8"));
  console.log(`Loaded ${raw.length} raw posts from ${inPath}`);

  const selected = selectAndDedup(raw);
  console.log(
    `After selecting fields + dedup on share_urn + dropping reposts/empty: ${selected.length} posts`
  );

  const features = buildFeatures(selected);

  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(features, null, 2), "utf8");

  console.log(`\nVolume check: ${features.volume_check.posts} posts ` +
    `(meets 80-post floor: ${features.volume_check.meets_floor})`);
  console.log(`Median engagement: ${features.engagement.median} · Median words: ${features.length.median_words}`);
  console.log(`\nWrote feature digest -> ${outPath}`);
}

main().catch((err) => {
  console.error("Fatal:", err.message);
  process.exit(1);
});
