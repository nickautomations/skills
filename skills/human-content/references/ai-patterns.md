# AI writing patterns

The catalog for the humanize pass and detect mode. These tells exist because language models drift toward the most statistically likely phrasing that fits the widest range of cases: generic, inflated, evenly paced. The fix in every case is the same move: state the specific point plainly and let the reader judge its weight.

Rewrite whole sentences around their point. Do not patch the flagged phrase and leave the sentence's shape intact.

## Words and phrases

**Cut outright:** delve, foster, leverage, utilize, facilitate, empower, streamline, robust, seamless, cutting-edge, game-changer, game-changing, transformative, paradigm shift, tapestry, realm, beacon, multifaceted, meticulous, intricate, paramount, elevate, embark, supercharge, harness, ever-evolving, landscape (abstract), testament, pivotal, crucial, showcase, underscore (verb), highlight (verb), interplay, vibrant, enduring, garner, unlock potential, unprecedented, in today's fast-paced world, gate/gated/gating (figurative). Two of these double as real technical vocabulary: "robust" and "gate/gated/gating" are tells only in their figurative sense ("a robust culture of trust"); keep them in technical or product use ("a robust retry policy", "gated content behind the signup form").

**Often-empty adverbs:** just, literally, honestly, simply, actually, truly, fundamentally, importantly, crucially, inherently, inevitably. Cut when they add nothing; keep when they carry real emphasis, uncertainty, contrast, or the writer's spoken rhythm.

**Filler phrases.** "In order to" becomes "to". "Due to the fact that" becomes "because". "At this point in time" becomes "now". "Has the ability to" becomes "can". "It is important to note that the data shows" becomes "the data shows". Same treatment for: it's worth noting, at the end of the day, when it comes to, at its core, in today's world, the reality is, in terms of, with regard to, going forward, let's dive in.

**Stacked qualifiers.** "It could potentially possibly be argued that the policy might have some effect" becomes "The policy may affect outcomes." Keep a qualifier only when the source supports it and the meaning needs it.

**Hyphenated-pair spam.** Keep the hyphen only where grammar needs it, before a noun: "a high-quality report", but "the report is high quality". Exception: compounds the dictionary always hyphenates, such as third-party and cross-functional, keep the hyphen in every position.

## Content patterns

**Inflated importance.** Watch for: stands as, serves as, marks a pivotal moment, plays a vital role, reflects broader, setting the stage for, key turning point, indelible mark, solidifies its position. Ordinary facts get dressed as milestones. "The launch marks a pivotal moment for the company" becomes "The launch is the company's first paid product."

**Sales language.** Watch for: boasts, nestled, in the heart of, breathtaking, stunning, renowned, must-visit, rich (figurative), commitment to. "Nestled in the breathtaking region of Gonder, the town stands as a vibrant community" becomes "The town is in the Gonder region of Ethiopia."

**Shallow -ing analysis.** A trailing participle phrase that pretends to explain meaning: highlighting, underscoring, reflecting, symbolizing, showcasing, fostering, ensuring. Replace with a real consequence or cut. "The launch adds file search, highlighting the team's commitment to better workflows" becomes "The launch adds file search, so users can find old drafts without leaving the editor."

**Vague or weasel attribution.** "Experts agree", "industry reports suggest", "many argue", "studies show", "widely regarded as". Name the source or cut the claim. Never invent a source; if none exists, ask.

**Vague relationship attribution.** "Associated with", "connected to", "linked to", "tied to" state that two things relate without saying how. "He is associated with the orchestra" becomes "He founded and conducts the orchestra." Name the real relationship the source gives; if the source doesn't say, leave the vague wording rather than inventing a role.

**Name-dropping as proof.** A list of famous outlets or a follower count with no context. Keep a citation only when it says what was said and where.

**Stock challenges-and-outlook sections.** "Despite these challenges... continues to thrive." Replace with the concrete facts, or cut the section.

**Knowledge-gap guessing.** "While details are scarce, it appears...", "she likely grew up...", "it is believed that". State what the sources do not show, or cut the sentence. Never present a guess as a fact.

## Sentence patterns

**Binary contrasts.** "It's not just X, it's Y." / "The question isn't X, it's Y." / "Not a X. Not a Y. A Z." State Y directly. "The question isn't the model. It's the eval." becomes "The eval matters more than the model." The same move can split across two sentences ("This doesn't mean X. It means Y.") or end in a clipped negative tail ("...done right, no guessing"); treat both the same as the one-line form.

**Forced groups of three.** "Innovation, inspiration, and industry insights." Triads used for completeness rather than content. Break the rhythm; say what is actually there. The same habit scales up to a paragraph: three short parallel facts or examples, each its own sentence, capped by a line that draws the lesson. Merge the strongest example into the surrounding argument instead of listing all three.

**False ranges.** "From the Big Bang to the cosmic web, from stars to dark matter" where X and Y form no real range. List the actual topics.

**Synonym cycling.** Renaming the same subject for variety ("the agent... the assistant... the tool"). If the clear word is right, repeat it.

**Repeated sentence openings.** Several sentences starting with the same subject. Merge sentences or lead with the action. Fix the pattern, not the word; the remaining sentence may still start with "She".

**Fake-strong verbs.** "Serves as a centralized hub for sponsor management" becomes "tracks sponsors, drafts, and due dates in one place". Prefer is, are, has when they are clearer.

**Passive voice and missing actors.** "The results are preserved automatically" becomes "The system preserves the results automatically." Say who acts.

**Dramatic fragmentation.** "No aesthetic prior. No nostalgia. The old rules were gone." One short sentence adds emphasis; a row of fragments is staging. Same for "That's it. That's the whole thing."

**Colon reveals.** Noun phrase, colon, dramatic reveal: "The best part: it learns." Rewrite as a plain sentence. Colons are for lists, labels, and quotes.

**Tailing negation.** "The options come from the selected item, no guessing." Write the clause: "...without forcing the user to guess."

## Rhetoric patterns

**Throat-clearing and fake-candid openers.** "Here's the thing", "Let me be clear", "Honestly?", "Look," "Real talk" as a staged pause before an ordinary point. Cut the opener, state the point. ("Honestly" mid-sentence in casual writing is fine; the tell is the standalone theatrical opener.)

**Announcing the next point.** "Let's dive into how caching works. Here's what you need to know." State the content instead. The casual version ("one thing that bit me hard, so pay attention:") is the same pattern; remove the announcement, not just its formal tone.

**Faux-insight setups.** "What most people get wrong", "here's what nobody tells you", "the part everyone misses". Cut the setup; the claim stands on its own. "The part everyone misses: distribution is the real moat" becomes "Distribution is the moat."

**Fake-deep framing.** "The real question is", "at its core", "what really matters", "the heart of the matter", and X-is-the-Y-of-Z sayings ("symmetry is the language of trust"). Replace the profundity with the specific claim.

**Interpretive metadiscourse.** Lines that step outside the subject to tell the reader what to notice: "That last part matters more than it sounds", "As you can see", "This distinction matters", redundant "in other words". Includes a line right after an example, scene, or number that spells out what it just proved: "This shows the importance of...", "It was a lesson in patience." If the point is clear, delete the aside; if not, add support instead.

**Answering objections nobody raised.** "This isn't mainly about X, and I'm not arguing Y." Unattributed defenses against absent critics. Keep an objection only when the text names its source or answers it in full; otherwise state the positive claim alone.

**Rejecting fake alternatives.** "A tempting approach would be... but". An option no reader would consider, introduced only to be dismissed, usually a leftover drafting artifact. Cut the fake option and state the real constraint.

**Rhetorical setups.** "What if I told you...", "Think about it:", "Plot twist:", self-answered question-answer pairs. Drop them and make the point.

**Fake-profound kickers.** A closing metaphor, aphorism, or mic-drop line. Delete it; do not rewrite it into a better metaphor. End on the clearest concrete sentence already in the draft, a plain takeaway, or a next action.

**Summary-recap endings and generic optimism.** "In conclusion", "Ultimately", a final paragraph restating the piece, or "the future looks bright" send-offs. The reader was just there. End on the last concrete point.

**Heading echoed in the first sentence.** A heading followed by a one-liner that restates it. Cut the echo.

## Formatting

- **Bold spam.** Bold sprinkled mid-sentence for emphasis, or list items that each open with a bold label and colon. Unbold, or fold the list into prose when two sentences would read better.
- **Emoji decoration** in headings and list items. Remove.
- **Title Case Headings.** Use sentence case.
- **Decorative structure.** A horizontal rule between every section, or a top-level heading that just repeats the document's own title, is decoration; drop both. A heading written for effect ("The decision, on one screen") should instead name what the section holds ("How the six options compare").
- **Curly quotes** where the writer or format uses straight quotes.
- **Em and en dashes.** Do not use them as a rhythm crutch. In short copy, none. In longer drafts, one or two only where they clearly beat commas, periods, or parentheses; remove clusters, spaced dashes, and double hyphens. A user's writing sample that uses them overrides this: match the sample's rate.
- **Over-structuring.** Headers over two-sentence sections, bullets where prose would flow. Format follows content.

## Chatbot artifacts

- **Leftover chat text.** "I hope this helps!", "Certainly!", "Would you like me to...", "Let me know if..." in text that should stand alone. Cut.
- **Agreeable padding.** "Great question! You're absolutely right that..." before the answer. Cut; keep only the substantive part.
- **Cutoff disclaimers.** "As of my last update...". Cut.
- **Writing about the document instead of its subject.** Docs and comments describe current behavior, not how the text got there or how it was put together. Cut narration of the old approach ("Added to replace the previous O(n²) approach" becomes "uses a hash map for O(1) lookups"; the old approach belongs only in changelogs and migration guides), of how the text was assembled or sourced ("generated from...", "compiled from...", "anything unconfirmed is flagged rather than guessed"), and of a layout or order the reader can already see ("the table below compares...", "this section is organized by owner"). Keep a source credit the reader can follow; cut the account of how you worked.

## Reader-context patterns

**Re-explaining what the reader already knows.** In a reply, comment, or thread, the reader already has the background; rebuilding it before the decision buries the point, even though each sentence reads fine on its own. Watch for a short reply that restates the problem, walks through the diagnosis, and reaches the decision only in the last line. Lead with the decision; keep only the fact or link that would change whether the reader agrees. The full diagnosis belongs in the ticket or document the reply points to, not in the reply itself.

## What NOT to flag

No single item below proves anything; look for several patterns stacked in one passage.

- Perfect grammar, consistent style, or dry prose. Polish is not AI; generic dryness without specific tells is just dry writing.
- Formal words in isolation. Only the specific overused words above count, and mostly in groups.
- One transition word, one em dash, one short punchy sentence, curly quotes alone. Editors and word processors produce all of these.
- Deliberate repeated openings that build rhythm ("She came. She saw. She conquered.").
- Useful scope statements, legal and safety notices, real corrections, named objections, FAQ answers.
- Real alternatives a reader might genuinely weigh in a design doc, tutorial, or argument.
- Watched phrases inside quotes, titles, proper names, or examples where the phrase is discussed rather than used.

## Human details to protect

Keep these unless they damage the meaning; they carry the writer's voice:

- Specific, unusual details: a real address, an odd quote, "the lawyer who used to work upstairs from my dentist".
- Mixed feelings and unresolved tension: "mostly good, but it bothers me and I can't explain why".
- Era-bound slang, memes, and in-jokes.
- Genuine asides, parentheticals, and self-corrections.
- Uneven sentence lengths and pace changes.
- A deliberate cut or word choice the writer could defend.
