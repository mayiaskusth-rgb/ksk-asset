# Transcript Intelligence Agent — Analysis Contract

**Version:** 0.1.0  
**Status:** Design specification; not implemented as an automated Python agent  
**Applies to:** YouTube Audience Intelligence Engine  
**Execution:** Human/model-assisted analysis of a collected, normalized transcript. No paid LLM API is assumed or authorized by this specification.

## Mission

Explain how a video communicates: what it teaches, how it structures curiosity, how it develops ideas, what tone and format it uses, how information is paced, and which techniques may be reusable in original content.

This is not a generic summarizer, a video-quality grader, or a script generator. The output must help a researcher understand the creator's communication choices and compare them across videos.

## Inputs and eligibility

Required:
- Video metadata: video ID, title, channel, URL, duration, publication date if known.
- Normalized transcript with timestamped segments.
- Transcript provenance: source adapter/version, language, caption type, retrieval time, status, checksum.
- Transcript quality assessment: coverage, gaps, timestamp availability, language confidence if known.

Optional:
- Description and chapters.
- Separately collected visual observations with timestamps and source.
- Separately collected audio/voice measurements with timestamps and method.

Do not analyze a transcript marked unavailable, empty, or materially truncated as if it were complete. A partial transcript may receive a clearly labeled partial analysis with confidence reduced.

## Analysis dimensions

### 1. Subject and conceptual map
- Central subject and the question the video addresses.
- Main thesis, answer, or takeaway (if one is actually present).
- Key concepts, entities, mechanisms, events and relationships.
- Prerequisite knowledge assumed.
- Explanations, examples, analogies and evidence used.
- Distinguish central concepts from passing mentions.

### 2. Content format and narrative mode
Use a multi-label taxonomy; do not force every video into one genre.

Possible format labels:
- documentary / journalistic explainer
- educational explainer
- mystery / reveal
- investigative
- narrative essay
- case study
- tutorial / demonstration
- list / countdown
- commentary / opinion
- interview / conversation
- review / comparison
- news update
- personal story
- compilation / reaction
- other / mixed

For each selected label provide a short reason and supporting timestamp(s). Separately describe narrative mode, such as chronological, question-led, problem-solution, claim-evidence, thematic, episodic, or list-based.

### 3. Hook and curiosity architecture
- Opening move and first meaningful promise/question.
- Curiosity mechanism: surprise, mystery, stakes, contradiction, scale, relatable problem, misconception, or another evidenced device.
- Open loops: question raised, when it is revisited, and whether it is resolved.
- Payoff: what the opening promised versus what the video delivered.
- Re-engagement beats throughout the video, with timestamps.

### 4. Structure and progression
Create a chronological section map with approximate start/end times and each section's role. Identify:
- setup, context, explanation, evidence, example, transition, reveal, recap and conclusion;
- changes in question or direction;
- escalation, contrast, callback and resolution;
- repeated or unresolved threads.

Do not force a conventional three-act structure if the transcript does not support it.

### 5. Explanation techniques
Identify concrete use of:
- analogy and metaphor;
- everyday examples and relatable comparisons;
- definitions and jargon translation;
- demonstrations or thought experiments (transcript evidence only);
- contrast, misconception reversal and scale;
- evidence, expert references, caveats and uncertainty;
- recap and signposting.

Explain what each technique does for comprehension. Flag leaps, ambiguity or unsupported assertions without attempting a full fact-check unless requested.

### 6. Tone, voice and rhetorical style
Describe observed language choices, not the creator's personality:
- conversational / formal / technical / journalistic;
- neutral / curious / humorous / dramatic / suspenseful / urgent / reflective;
- first-person, direct address, rhetorical questions;
- hedging, qualification, certainty and credibility construction;
- sentence and paragraph rhythm;
- memorable phrasing (short excerpts only).

Tone labels may coexist. Every non-obvious label needs textual evidence.

### 7. Pacing and information density
Keep three ideas separate:

1. **Speech rate:** estimated words per minute over timestamped windows, only when timestamps and transcript quality support it.
2. **Information density:** how many new concepts, facts or claims are introduced in a section.
3. **Narrative pace:** how quickly the video changes question, section, example, reveal or story beat.

Report relative changes (slower setup, dense explanation, rapid sequence of examples) rather than declaring a universal ideal pace. Caption timestamps can be coarse, repeated or auto-generated; never present precise speech-rate metrics without a method and quality warning. Transcript alone cannot measure editing pace, visual cuts, music, silence or delivery energy.

### 8. Strong moments and reusable techniques
Select up to five evidence-backed moments. For each: timestamp, concise paraphrase, technique, why it may help comprehension or curiosity, and confidence.

Then separate:
- reusable communication principle;
- topic-specific content that should not be copied;
- possible adaptation to a different topic/audience;
- unanswered question or angle for further research.

### 9. Limitations and confidence
Report missing/weak evidence, transcript completeness, language, caption type, timing quality, unavailable visual/audio data, and any inference that remains uncertain.

Use confidence per finding where practical (high / medium / low) and explain the basis. Do not output one opaque overall quality score.

## Evidence and safety rules

- Claims about a specific moment, hook, section, quote, technique or sequence require timestamp evidence.
- Use short excerpts; prefer paraphrase. Never reproduce long transcript passages.
- Distinguish **observation** (what the source says), **interpretation** (what technique it represents), and **hypothesis** (why it may work).
- Do not invent missing words, timestamps, scenes, visuals, music, audience reactions or creator intent.
- Do not claim that a technique improved retention, CTR, satisfaction or performance without corresponding evidence.
- Do not infer visual pacing, camera work, editing or vocal energy from text alone.
- Do not treat transcript-derived sentiment or tone as a factual description of the creator.
- Treat transcripts as copyrighted source material: retain only what is needed for private analysis, do not publish full transcripts, and keep private run artefacts out of this public repository.
- Avoid unnecessary personal data from speakers or interview subjects.

## Output structure

1. Source and transcript quality
2. One-paragraph video overview
3. Central question, thesis and concept map
4. Format labels and narrative mode
5. Hook, open loops and payoff
6. Timestamped structure map
7. Explanation techniques
8. Tone and rhetorical style
9. Pacing and information density
10. Strong moments (up to five)
11. Reusable techniques and adaptation ideas
12. Unanswered questions / opportunity hypotheses
13. Limitations and confidence

## Comparative analysis

Compare videos only after individual analyses exist. Prefer a deliberate comparison set (e.g. an outlier and ordinary performers from the same topic or creator cohort). Compare like with like:
- topic and audience intent;
- format and duration;
- transcript completeness and caption type;
- publication age where relevant.

Compare specific techniques and their evidence, not a vague "better video" score. Report recurring patterns, differences, counterexamples and uncertainty. A small sample supports hypotheses, not universal rules or causal conclusions.

## Versioning

This rubric is versioned. After a small pilot batch, collect user feedback and revise with a changelog. Do not silently change the taxonomy or scoring semantics. No numeric quality score is part of v0.1.
