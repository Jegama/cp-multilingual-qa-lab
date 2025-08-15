# **Sermon Evaluation Framework**

This framework defines a two–step process for evaluating Christian sermons (expository / Christ‑centered) in a structured, reproducible way. Based on Bryan Chappell's book, Christ-Centered Preaching.

---

## Overview of the Two-Step Process

1. **Step 1 – Descriptive Extraction (Structural Analysis)**  
	 The model parses the sermon transcript and produces a rich descriptive JSON object capturing introductions, proposition, main points (with sub‑points, illustrations, applications, comments, feedback), general comments, the Fallen Condition Focus (FCF), and a confidence score.

2. **Step 2 – Analytical Scoring (Synthesis & Coaching)**  
	 Using the structured Step 1 output, the model assigns 1–5 scores across higher‑level qualitative criteria (textual fidelity, proposition clarity, FCF identification, Christ‑centeredness, application effectiveness, structure cohesion, illustration quality, pastoral tone, overall impact) and produces strengths, growth areas, and actionable next steps.

Both steps MUST be deterministic (temperature ≈ 0 for structural extraction) and always return valid JSON.

---

## Scoring Scale (Step 2)
| Score | Meaning |
| ----- | ------- |
| 5 | Exemplary: precise, text‑grounded, Christ‑centered, compelling, pastorally rich. |
| 4 | Strong: minor omissions or mild unevenness. |
| 3 | Adequate: clear basics present, lacks depth or consistency. |
| 2 | Deficient: important elements unclear, shallow, or partially inaccurate. |
| 1 | Problematic: major inaccuracies, missing essentials, or misleading emphasis. |

---

## Step 1 Criteria & Sub-Criteria (Descriptive Extraction Fields)

### 1. Scripture Introduction
* Identifies the primary biblical text(s) accurately (reference + translation clarity).  
* Provides immediate textual orientation: genre, context, setting, speaker, audience.  
* Frames why this text matters today (bridging ancient context to present need).  
* Avoids unrelated anecdotes before grounding in Scripture.

### 2. Sermon Introduction
* Engages interest without overshadowing the text.  
* Surfaces a tension / need / question that the passage resolves.  
* Naturally narrows toward the Proposition and (implicitly or explicitly) the FCF.  
* Avoids moralistic clichés detached from the text.

### 3. Proposition
* A single, clear, declarative summary of the sermon's message (subject + complement).  
* Text‑derived (not imposed).  
* Christ‑centered orientation preferred where text warrants.  
* If missing or implied, note deficiency with specificity.  
* Evaluate precision (vagueness, over‑complexity, multiple competing propositions).

### 4. Body (Main Points Collection)
For each main point:
* **Point**: Stated as an imperative, indicative, or doctrinal truth; clearly anchored to a discrete textual segment (verse(s) indicated).  
* **Summary**: Expanded explanation faithful to context (literary + redemptive).  
* **Subpoints**: Coherent logical development; if absent, note consciously.  
* **Illustrations**: Relevant, accurate, and in service of the point—not entertainment; Scripture quotations are NOT illustrations.  
* **Application**: Specific, grace‑motivated, heart + life oriented (not generic moralism).  
* **Comments**: Evaluate exegesis fidelity, clarity, progression toward climax, over‑proof‑texting risks, handling of original audience.  
* **Feedback**: Constructive, actionable coaching (what to refine, add, trim, rephrase, or reorder).  

### 5. General Comments
* **Content Comments**: Doctrinal substance? Faithful synthesis? Christ and Gospel explicit where warranted?  
* **Structure Comments**: Logical flow, unity, escalation, transitions, balance of explanation vs. application.  
* **Explanation Comments**: Depth of exegesis, context (historical, literary), handling of difficult phrases, theological integration.

### 6. Fallen Condition Focus (FCF)
* **FCF**: The shared human brokenness, limitation, or need (not always explicit sin) addressed by the text. Specific and text‑rooted.  
* **Comments**: Distinguish between surface problem and deeper gospel issue; confirm alignment with main points and applications; guard against purely behavioral framing; note if FCF is missing, too broad, or misaligned.

### 7. Confidence Score
* A floating value (0–1) reflecting internal model confidence in extraction accuracy.  
* Should consider transcript completeness, clarity, audio artifacts (if hinted), structural ambiguity, or missing proposition.

---

## Step 2 Analytical Rubric (Detailed Quantitative Scoring)

Step 2 converts the rich descriptive output (Step 1) into granular rubric‑based scores (1–5) plus qualitative feedback per category. The original flat snake_case score keys have been replaced with human‑readable nested JSON objects (mirroring naming style of other evaluation frameworks). Every score MUST be an integer 1–5 (5 = absolutely yes / exemplary; 1 = absolutely no / absent / severely deficient). After per‑criterion scoring, an aggregated summary may be produced (see Aggregated Summary section).

### A. Introduction
Sub‑Criteria:
1. FCF Introduced (derives a specific Fallen Condition from the preached text)
2. Arouses Attention (meaningful, text‑relevant interest / tension builder)
Feedback: Holistic, actionable coaching (affirm + improve).

### B. Proposition
Sub‑Criteria:
1. Principle + Application Wed (subject + complement actionable)
2. Establishes Main Theme (governs entire sermon)
3. Summarizes Introduction (concept & key terminology continuity)
Feedback: Strengths + surgical improvements.

### C. Main Points
Sub‑Criteria:
1. Clarity (succinct, memorable wording)
2. Hortatory Universal Truths (principial, not purely narrative recap)
3. Proportional & Coexistent (balanced; logical symmetry)
4. Exposition Quality (text sufficiently explained)
5. Illustration Quality (illumines; not distracts; text‑serving)
6. Application Quality (specific, grace‑motivated)
Feedback: Cohesion, pacing, balance suggestions.

### D. Exegetical Support
Sub‑Criteria:
1. Alignment with Text (sermon reflects passage burden)
2. Handles Difficulties (addresses key interpretive tensions)
3. Proof Accuracy & Clarity (supporting reasoning sound & digestible)
4. Context & Genre Considered (literary + redemptive location honored)
5. Not Belabored (stops when sufficiently proven)
6. Aids Rather Than Impresses (service over display)
Feedback: Depth vs brevity, clarity, balance.

### E. Application
Sub‑Criteria:
1. Clear & Practical (concrete, lived pathways)
2. Redemptive Focus (Christ / grace motive vs moralism)
3. Mandate vs Idea Distinction (authority clarity)
4. Passage Supported (derives organically)
Feedback: Sharpen, contextualize, motivate.

### F. Illustrations
Sub‑Criteria:
1. Lived‑Body Detail (sensory, credible, incarnational texture)
2. Strengthens Points (illumination of stated truth)
3. Proportion (economy; pacing; length)
Feedback: Trim / diversify / anchor to text.

### G. Conclusion
Sub‑Criteria:
1. Summary (concise recapitulation)
2. Compelling Exhortation (specific gospel call / response)
3. Climax (crescendo; theological / pastoral apex)
4. Pointed End (decisive, purposeful landing)
Feedback: Intensify, focus, seal.

### H. Confidence
* confidence_score – Float 0–1 reflecting evaluator confidence in Step 2 scoring fidelity (quality of Step 1 data, transcript clarity, structural ambiguity, etc.).

### Scoring Guidance (Heuristic)
| Score | Descriptor | Heuristic Examples |
| ----- | ---------- | ------------------ |
| 5 | Exemplary | Fully present; text‑anchored; pastorally effective; no substantive improvement needed. |
| 4 | Strong | Minor refinement possible (brevity, nuance) but solid. |
| 3 | Adequate | Present yet uneven, generic, or partially diluted. |
| 2 | Weak | Significant gaps: unclear, forced, thin, or inconsistent. |
| 1 | Deficient | Absent, inaccurate, misleading, or counter‑productive. |

### Aggregated Summary

Compute rolled‑up composite categories for dashboards by averaging related raw scores:
* Textual_Fidelity ≈ avg(Exegetical Support.Alignment with Text, Handles Difficulties, Proof Accuracy & Clarity, Context & Genre Considered)
* Proposition_Clarity ≈ avg(Proposition.Principle + Application Wed, Establishes Main Theme, Summarizes Introduction)
* FCF_Identification ≈ Introduction.FCF Introduced (optionally cross‑checked against Step 1 FCF extraction)
* Application_Effectiveness ≈ avg(Application.Clear & Practical, Redemptive Focus, Mandate vs Idea Distinction, Passage Supported, Main Points.Application Quality)
* Structure_Cohesion ≈ avg(Main Points.Proportional & Coexistent, Conclusion.Summary, Conclusion.Compelling Exhortation, Conclusion.Climax, Conclusion.Pointed End)
* Illustrations ≈ avg(Main Points.Illustration Quality, Illustrations.Lived-Body Detail, Illustrations.Strengthens Points, Illustrations.Proportion)
* Pastoral_Tone (optional) – inferred qualitatively from feedback text; not directly scored in rubric (retain only if needed for parity with other frameworks).
* Overall_Impact – computed narrative / weighted synthesis (NOT a simple average—explain rationale).

---

### Rubric Table (Step 2 – Example Format)

Each top‑level category contains its sub‑criteria as keys with spaces. Feedback resides under the same category. Confidence is a top‑level scalar.

| Category | Sub‑Criterion | Sermon A | Sermon B |
| -------- | ------------- | -------- | -------- |
| Introduction | FCF Introduced | 5 | 4 |
|  | Arouses Attention | 4 | 3 |
|  | Feedback | Strong tension; trim hook | Less focus |
| Proposition | Principle + Application Wed | 5 | 4 |
|  | Establishes Main Theme | 5 | 5 |
|  | Summarizes Introduction | 5 | 3 |
|  | Feedback | Crisp & repeatable | Needs terminological alignment |
| Main Points | Clarity | 5 | 4 |
|  | Hortatory Universal Truths | 4 | 3 |
|  | Proportional & Coexistent | 4 | 3 |
|  | Exposition Quality | 5 | 4 |
|  | Illustration Quality | 3 | 2 |
|  | Application Quality | 4 | 3 |
|  | Feedback | Solid structure; tighten illus. 2 | Needs clearer imperatives |
| Exegetical Support | Alignment with Text | 5 | 4 |
|  | Handles Difficulties | 4 | 3 |
|  | Proof Accuracy & Clarity | 5 | 4 |
|  | Context & Genre Considered | 4 | 3 |
|  | Not Belabored | 5 | 5 |
|  | Aids Rather Than Impresses | 5 | 4 |
|  | Feedback | Text governs sermon | Trim ornamental detail |
| Application | Clear & Practical | 4 | 3 |
|  | Redemptive Focus | 5 | 4 |
|  | Mandate vs Idea Distinction | 4 | 2 |
|  | Passage Supported | 3 | 3 |
|  | Feedback | Gospel‑driven; label mandates | Clarify authority level |
| Illustrations | Lived‑Body Detail | 4 | 3 |
|  | Strengthens Points | 4 | 3 |
|  | Proportion | 3 | 2 |
|  | Feedback | Trim length & diversify | Reduce anecdote weight |
| Conclusion | Summary | 5 | 4 |
|  | Compelling Exhortation | 4 | 3 |
|  | Climax | 4 | 2 |
|  | Pointed End | 5 | 4 |
|  | Feedback | Strong landing; heighten climax | Sharpen summons |
| Confidence | Confidence | 0.90 | 0.78 |

---

## Common Strength Indicators
* Proposition is concise, text‑anchored, repeatable.  
* FCF is narrow enough to drive structure yet broad enough to connect pastorally.  
* Clear redemptive arc culminating in Christ’s person/work.  
* Applications flow organically from exposition (not bolted on).  
* Illustrations illuminate, not entertain; minimal redundancy.  
* Balanced exposition: neither word‑study overload nor shallow gloss.

## Common Failure Modes
* Missing or nebulous proposition (multiple competing themes).  
* Moralistic applications detached from grace/redemption.  
* Overuse of disconnected cross‑references (listener fatigue).  
* FCF stated as a vague universal (“we all struggle”) with no textual tether.  
* Illustrations that overshadow the point or introduce doctrinal confusion.  
* Christ absent where text trajectory clearly points to Him (e.g., redemptive-historical pivot texts).  
* Applications purely behavior‑control without gospel motivation.

---

## Example Partial Evaluation Table (Derived Aggregations)

| Aggregated Criterion | Value |
| --------------------- | ----- |
| Textual_Fidelity | 4.25 |
| Proposition_Clarity | 5.0 |
| FCF_Identification | 5 |
| Application_Effectiveness | 3.6 |
| Structure_Cohesion | 4.2 |
| Illustrations | 3.7 |
| Overall_Impact | 4 |

---

## Step 1 Example JSON Output

```json
{
	"scripture_introduction": "Today we examine Ephesians 2:1-10, where Paul contrasts spiritual death with the grace that makes us alive in Christ...",
	"sermon_introduction": "The preacher opens with a relatable scenario about striving for approval, leading into humanity's deeper need for mercy...",
	"proposition": "God graciously makes the spiritually dead alive in Christ so that His grace, not our works, defines our future.",
	"body": {
		"main_points": [
			{
				"point": "1. Our Natural Condition: Dead in Trespasses (vv. 1-3)",
				"summary": "Explains spiritual death—alienation from God, enslaved to world, flesh, devil.",
				"subpoints": ["Death described (v1)", "Enslavement (v2)", "Deserving wrath (v3)"],
				"illustrations": ["Hospital code-blue analogy"],
				"application": "Invites honest acknowledgment of helplessness; abandon self-salvation.",
				"comments": "Faithful to text; could nuance 'wrath' pastoral tone a bit more.",
				"feedback": "Clarify difference between total inability vs. utter worthlessness (avoid shame framing)."
			},
			{
				"point": "2. God’s Merciful Intervention (vv. 4-7)",
				"summary": "Unpacks 'But God' pivot—rich mercy, great love, made alive, raised, seated.",
				"subpoints": ["But God (v4)", "Made alive (v5)", "Raised & seated (v6-7)"],
				"illustrations": ["Judge adopting the guilty"],
				"application": "Assures believers of secure identity; fuels humility.",
				"comments": "Christ-union well explained; slight overuse of adoption imagery not in immediate text.",
				"feedback": "Tie exaltation (v6) more explicitly to corporate church dimension."
			},
			{
				"point": "3. Grace Defines Our Purpose (vv. 8-10)",
				"summary": "Explores salvation by grace through faith leading to prepared good works.",
				"subpoints": ["Gift nature (v8-9)", "Workmanship & mission (v10)"],
				"illustrations": ["Restoration of a masterpiece"],
				"application": "Encourages serving from acceptance, not for it.",
				"comments": "Accurate; could reference faith as instrument not merit.",
				"feedback": "Short clarifier on 'works prepared beforehand' avoiding hyper-determinism misunderstanding."
			}
		]
	},
	"general_comments": {
		"content_comments": "Doctrinally sound; consistent Pauline theology; rich union-with-Christ emphasis.",
		"structure_comments": "Three-point arc mirrors text structure; transitions mostly smooth.",
		"explanation_comments": "Greek nuances paraphrased understandably; could briefly note audience (Ephesus Gentiles)."
	},
	"fallen_condition_focus": {
		"fcf": "Human spiritual deadness & self-reliant striving that ignores need for resurrecting grace.",
		"comments": "Well-specified; fuels urgency of divine initiative and shapes grace-centered applications."
	},
	"confidence_score": 0.92
}
```

## Step 2 Example JSON Output

```json
{
	"Introduction": {
		"FCF Introduced": 5,
		"Arouses Attention": 4,
		"Feedback": "Strong tension; trim hook by ~20% for pacing."
	},
	"Proposition": {
		"Principle + Application Wed": 5,
		"Establishes Main Theme": 5,
		"Summarizes Introduction": 5,
		"Feedback": "Memorable; consistent terminology reinforces cohesion."
	},
	"Main Points": {
		"Clarity": 5,
		"Hortatory Universal Truths": 4,
		"Proportional & Coexistent": 4,
		"Exposition Quality": 5,
		"Illustration Quality": 3,
		"Application Quality": 4,
		"Feedback": "Structure text-driven; shorten 2nd illustration; specify vocational application in point 3."
	},
	"Exegetical Support": {
		"Alignment with Text": 5,
		"Handles Difficulties": 4,
		"Proof Accuracy & Clarity": 5,
		"Context & Genre Considered": 4,
		"Not Belabored": 5,
		"Aids Rather Than Impresses": 5,
		"Feedback": "Minor historical nuance (audience background) could deepen relevance."
	},
	"Application": {
		"Clear & Practical": 4,
		"Redemptive Focus": 5,
		"Mandate vs Idea Distinction": 4,
		"Passage Supported": 3,
		"Feedback": "Highlight which exhortations are wisdom vs mandate; tighten text tie in final movement."
	},
	"Illustrations": {
		"Lived-Body Detail": 4,
		"Strengthens Points": 4,
		"Proportion": 3,
		"Feedback": "One narrative risks overshadowing exposition; diversify with a shorter contrast example."
	},
	"Conclusion": {
		"Summary": 5,
		"Compelling Exhortation": 4,
		"Climax": 4,
		"Pointed End": 5,
		"Feedback": "Clear gospel landing; consider amplifying resurrection link for emotional ascent."
	},
	"Confidence": 0.90,
	"Strengths": [
		"Text tightly governs structure",
		"Crisp, repeated proposition",
		"Grace-centered, non-moralistic application"
	],
	"Growth Areas": [
		"Trim second illustration length",
		"Clarify mandate vs wisdom distinction",
		"Add a brief socio-historical audience note"
	],
	"Action Steps": [
		"Reduce illustration 2 by ~25%",
		"Insert one-sentence Ephesian context after reading",
		"Label at least one application explicitly as wisdom guidance"
	]
}
```

---

## Step 1 JSON Schema
```json
{
	"scripture_introduction": "string",
	"sermon_introduction": "string",
	"proposition": "string",
	"body": {
		"main_points": [
			{
				"point": "string",
				"summary": "string",
				"subpoints": ["string"],
				"illustrations": ["string"],
				"application": "string",
				"comments": "string",
				"feedback": "string"
			}
		]
	},
	"general_comments": {
		"content_comments": "string",
		"structure_comments": "string",
		"explanation_comments": "string"
	},
	"fallen_condition_focus": {
		"fcf": "string",
		"comments": "string"
	},
	"confidence_score": 0.0
}
```

### Step 2 JSON Schema
```json
{
	"Introduction": {
		"FCF Introduced": 0,
		"Arouses Attention": 0,
		"Feedback": "string"
	},
	"Proposition": {
		"Principle + Application Wed": 0,
		"Establishes Main Theme": 0,
		"Summarizes Introduction": 0,
		"Feedback": "string"
	},
	"Main Points": {
		"Clarity": 0,
		"Hortatory Universal Truths": 0,
		"Proportional & Coexistent": 0,
		"Exposition Quality": 0,
		"Illustration Quality": 0,
		"Application Quality": 0,
		"Feedback": "string"
	},
	"Exegetical Support": {
		"Alignment with Text": 0,
		"Handles Difficulties": 0,
		"Proof Accuracy & Clarity": 0,
		"Context & Genre Considered": 0,
		"Not Belabored": 0,
		"Aids Rather Than Impresses": 0,
		"Feedback": "string"
	},
	"Application": {
		"Clear & Practical": 0,
		"Redemptive Focus": 0,
		"Mandate vs Idea Distinction": 0,
		"Passage Supported": 0,
		"Feedback": "string"
	},
	"Illustrations": {
		"Lived-Body Detail": 0,
		"Strengthens Points": 0,
		"Proportion": 0,
		"Feedback": "string"
	},
	"Conclusion": {
		"Summary": 0,
		"Compelling Exhortation": 0,
		"Climax": 0,
		"Pointed End": 0,
		"Feedback": "string"
	},
	"Confidence": 0.0,
	"Strengths": ["string"],
	"Growth Areas": ["string"],
	"Action Steps": ["string"]
}
```

NOTE: Keys intentionally contain spaces for readability (valid in JSON). Downstream parsers should treat them as string literals.


## Aggregated Summary JSON Schema

```json
{
	"Aggregated": {
		"Textual_Fidelity": 0.0,
		"Proposition_Clarity": 0.0,
		"FCF_Identification": 0.0,
		"Application_Effectiveness": 0.0,
		"Structure_Cohesion": 0.0,
		"Illustrations": 0.0,
		"Overall_Impact": 0.0
	}
}
```

---

## Implementation Notes
* Step 1 should avoid invented content—only infer from transcript context; mark clearly if data is absent (e.g., "No explicit proposition stated").  
* Use consistent verse notation (e.g., "Eph 2:1-3").  
* Avoid labeling ordinary scripture quotations as illustrations.  
* In applications, privilege grace-driven transformation over mere behavioral exhortation.  
* Confidence score rationale (internal) should consider ambiguity signals; do not expose rationale in JSON.  
* Maintain strict JSON validity (double quotes, no trailing commas).  
* Keep categories stable for downstream parsers.

---

## Usage Summary
1. Run Step 1 extraction on transcript.  
2. Optionally convert Step 1 JSON to Markdown for human reviewers.  
3. Run Step 2 scoring referencing extracted fields (never re-parsing raw transcript if structured data sufficient).  
4. Present combined report (markdown + both JSONs) or persist to storage as needed.

---

This framework ensures consistent, Christ-centered, text-faithful sermon evaluation and constructive coaching feedback.
