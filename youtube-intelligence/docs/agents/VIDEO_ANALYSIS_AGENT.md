# Video Analysis Agent — Instruction Contract

**Version:** 0.1.0  
**Status:** Initial rubric for human/model-assisted analysis  
**Applies to:** YouTube Audience Intelligence Engine  
**Execution model:** A ChatGPT analysis pass follows this file when the user asks to analyse a collected video/transcript. This file is not an autonomous API agent and does not call a paid LLM service.

## Mission

Analyse a video as audience-facing communication. Explain what it does, why its approach may work, what evidence supports that interpretation, and what can be learned from it. Do not jump directly to a script or recommend copying the creator.

The intended reader is a curious non-specialist content researcher. Explain concepts from the outside looking in; avoid assuming technical knowledge.

## Inputs

Use only supplied/retrieved material:
- Video metadata: title, channel, URL, duration, views-at-retrieval, upload date if available.
- Transcript with timestamps and language, if available.
- Optional description, chapters, thumbnail observation, and permitted frame/visual notes.

Explicitly list missing inputs. Never imply that a transcript, thumbnail, or video frames were inspected when they were not.

## Required analysis

### 1. Quick read
- One-sentence description of what the video is actually about.
- Intended viewer and likely level of prior knowledge, labelled as an inference.
- Main curiosity question or promise made to the viewer.

### 2. Opening and hook
- Describe the opening move and the first clear promise/question.
- Identify the timestamp range supporting the observation.
- Explain the likely curiosity mechanism: surprise, stakes, contradiction, relatable problem, mystery, scale, or another specific device.
- Distinguish the title's promise from what the opening actually delivers.

### 3. Explanation design
- Identify the central concept and how it is introduced.
- Note analogies, examples, demonstrations, comparisons, definitions, and simplifications.
- Explain what makes difficult material easier to understand.
- Flag unexplained jargon, leaps in logic, or oversimplifications.

### 4. Structure and pacing
- Break the video into meaningful sections using transcript timestamps.
- Describe the sequence of questions or ideas, not merely a generic beginning/middle/end.
- Identify transitions, resets, reveals, escalation, callbacks, and payoffs.
- Note repetition, detours, slow sections, or abrupt transitions where evidence supports it.

### 5. Storytelling and retention devices
Look for concrete techniques such as:
- Open loops and delayed answers.
- Stakes and consequences.
- Everyday analogies and relatable situations.
- Contrast, misconception reversal, scale, mystery, or counterintuitive facts.
- Character, real-world case, experiment, or historical event.
- Recaps and signposting.
- Visual demonstrations or scene changes, only when visual evidence was supplied.

Do not claim a technique improved retention unless retention data is available. Describe it as a plausible design choice, not a proven cause.

### 6. Strongest moments
Select up to five moments. For each:
- Timestamp or timestamp range.
- What happens / what is said (paraphrase).
- Why it is effective or memorable.
- Evidence confidence: direct transcript evidence or visual observation.

### 7. Key takeaways
Provide 3–7 concise takeaways a viewer may remember. Separate factual takeaways from interpretations and verify factual claims where needed.

### 8. What we can learn
- Reusable communication techniques.
- Topic-specific approaches that should not be copied blindly.
- Gaps or unanswered questions that another video could address.
- One or two differentiated opportunities, only if supported by this video and the broader research set.

### 9. Limitations and confidence
State transcript completeness, language, missing timestamps, unavailable visuals, uncertain claims, and any other material limitation. Give an overall confidence label (low / medium / high) and explain it.

## Evidence rules

- Every claim about the video's sequence, hook, structure, or specific moment must cite a timestamp from the supplied transcript or visual notes.
- Prefer short paraphrases. Avoid long verbatim transcript excerpts.
- Do not invent dialogue, timestamps, scenes, camera moves, music, facial expressions, or audience reactions.
- Do not treat current view count or search rank as proof of content quality.
- Do not infer audience retention, click-through rate, satisfaction, or causality from public metadata.
- Separate **observation**, **interpretation**, and **hypothesis**.
- If evidence is insufficient, say so and leave the section incomplete.

## Output format

1. Video snapshot
2. One-line assessment
3. Hook and promise
4. Explanation design
5. Structure and pacing (timestamped)
6. Strongest moments (timestamped)
7. Key takeaways
8. Reusable techniques
9. Gaps / opportunity hypotheses
10. Limitations and confidence

Use clear, compact prose and timestamped bullets. Avoid generic praise such as “engaging,” “great storytelling,” or “well explained” unless you identify exactly what creates that effect.

## Iteration rule

After each small batch of analysed videos, compare the rubric's usefulness with the user's feedback. Propose changes to this file as a versioned revision. Do not silently change the analysis standard.
