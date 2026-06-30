## Architecture Narrative

1- A user submits a text to the platform. The platform sends that text to the `POST /submit` content submission endpoint.

2- First, the submission endpoint receives the raw text and checks that it is valid. The validation component makes sure the text is not empty, is within the allowed length, and can be analyzed.

3- Next, the validated text enters the detection pipeline. The detection pipeline sends the same text through two separate signal analyzers. Signal 1 measures one property of the text, and Signal 2 measures a different property. Each signal analyzer returns its own score.

4- After both signal scores are produced, the confidence scorer combines them into one overall attribution result and confidence score. The confidence score shows how certain the system is, instead of only returning a simple human-or-AI answer.

5- Then, the label generator uses the attribution result and confidence score to create a transparency label. This label is written in plain language so readers can understand whether the text appears human-written, appears AI-generated, or is uncertain.

6-Before the response is returned, the audit log records the decision. It stores the submitted content ID, the signal scores, the final attribution result, the confidence score, the transparency label, and the timestamp.

7- Finally, the API response is sent back to the platform. The platform can then display the transparency label to users.

## 2 detection signals:

Signal 1: Repetition / Generic Pattern Score

- What property of the text it measures:
  How often the text repeats similar words, phrases, sentence structures, or safe/generic ideas.
- Why that property differs between human and AI writing:
  AI writing can sometimes sound very smooth but repetitive. It may reuse similar transitions, balanced sentence patterns, or broad phrases instead of specific, personal, unusual details.
- What it can't capture (every signal has blind spots):
  Some human writers are naturally repetitive, especially in poems, speeches, or simple writing. Also, some AI writing can be edited to sound less repetitive.

Signal 2: Sentence Variation / Burstiness Score

- What property of the text it measures:
  How much the sentence length and structure changes across the text.
- Why that property differs between human and AI writing:
  Human writing often has more uneven rhythm: short sentences, long sentences, fragments, sudden changes, and personal style. AI writing may be more consistent and evenly structured.
- What it can't capture (every signal has blind spots):
  A careful human writer or a person with English Literature background may write very polished, even sentences. Also, creative AI prompts can produce varied sentence lengths, so this signal is not always reliable.

## Confidence Score Explanation:

The system combines both signal scores by averaging them into a single confidence score. This approach gives equal weight to each signal because they measure different aspects of the text: lexical repetition and sentence structure. If this project were deployed in a production system, additional signals and learned weighting would likely improve accuracy.

## Transparency Labels

### High-confidence AI

This text shows strong patterns associated with AI-generated writing.

### High-confidence Human

This text shows strong patterns associated with human-written work.

### Uncertain

This text has mixed signals. We cannot confidently determine whether it was human-written or AI-generated.

## Confidence Score Label

0.70 – 1.00 Likely AI
0.36 – 0.69 Uncertain
0.00 – 0.35 Likely Human

## Rate Limit Explanation:

The submission endpoint is limited to 10 requests per minute and 100 requests per day. This allows legitimate users to submit multiple pieces of writing while preventing automated abuse or large-scale scraping attempts

## Edge cases:

1- Poetry may be falsely flagged because repetition can be intentional.
2- Formal academic writing may look AI-like because sentence structure is polished and consistent.

## False positive problem: What happens when your system misclassifies a human writer's work:

A false positive happens when a human writer submits original work, but the system incorrectly classifies it as AI-generated.
The writer submits their text through POST /submit. The validation component accepts the text and sends it into the detection pipeline. Signal 1 and Signal 2 may return scores that make the text look somewhat AI-like. Possibly because the writing is polished, repetitive, or has consistent sentence structure.

The confidence scorer combines those signal scores, but because the evidence is not perfect, the system should not return a fully certain result. For example, if the confidence score is around 0.60, the label should reflect uncertainty instead of accusing the creator. The transparency label might say: “This text shows some patterns associated with AI-generated writing, but the result is uncertain.”

The creator sees the label and disagrees because they wrote the text themselves. They submit an appeal through POST /appeal, including the content ID and their explanation. The appeal handler updates the content status to under review.

The audit log records both the original classification and the appeal. It stores the original signal scores, confidence score, label text, creator reasoning, new status, and timestamp. This protects the creator by making the decision reviewable instead of final.

## API endpoints:

## API Surface

### 1. `POST /submit`

Purpose:
Accepts a piece of text and returns an attribution analysis.
Accepts:

```json
{
  "text": "The submitted poem, story, or blog post goes here.",
  "creator_id": "creator_123"
}
```

Returns:

```json
{
  "content_id": "content_001",
  "result": "uncertain",
  "confidence_score": 0.62,
  "label": "This text shows some patterns associated with AI-generated writing, but the result is uncertain.",
  "status": "classified"
}
```

---

### 2. `POST /appeal`

Purpose:
Allows a creator to contest a classification.

Accepts:

```json
{
  "content_id": "content_001",
  "creator_id": "creator_123",
  "creator_reasoning": "I wrote this myself and can provide drafts or notes."
}
```

Returns:

```json
{
  "appeal_id": "appeal_001",
  "content_id": "content_001",
  "status": "under_review",
  "message": "Your appeal has been received and the content is now under review."
}
```

---

### 3. `GET /log`

Purpose:
Returns structured audit log entries.

Returns:

```json
[
  {
    "event_type": "classification",
    "content_id": "content_001",
    "result": "uncertain",
    "confidence_score": 0.62,
    "signals_used": ["repetition_score", "sentence_variation_score"],
    "timestamp": "2026-06-27T10:30:00Z"
  },
  {
    "event_type": "appeal",
    "content_id": "content_001",
    "appeal_id": "appeal_001",
    "status": "under review",
    "appeal_reasoning": "I wrote this myself and can provide drafts or notes.",
    "timestamp": "2026-06-27T10:40:00Z"
  }
]
```

---

### 4. `GET /content/{content_id}`

Purpose:
Returns the current classification and review status for one piece of content.

Returns:

```json
{
  "content_id": "content_001",
  "result": "uncertain",
  "confidence_score": 0.62,
  "label": "This text shows some patterns associated with AI-generated writing, but the result is uncertain.",
  "status": "under review"
}
```

## Architecture Diagram

### Submission Flow

```text
User / Platform
   |
   | raw text + creator_id
   v
POST /submit
   |
   | submission request
   v
Rate Limiter
   |
   | allowed request
   v
Validation Component
   |
   | validated clean text
   v
Detection Pipeline
   |
   | clean text
   |----------------------------|
   v                            v
Signal 1: Repetition /          Signal 2: Sentence Variation /
Generic Pattern Score           Burstiness Score
   |                            |
   | signal 1 score             | signal 2 score
   |-------------|--------------|
                 v
Confidence Scorer
   |
   | combined score + attribution result
   v
Transparency Label Generator
   |
   | label text + confidence score + result
   v
Audit Log
   |
   | saved decision record
   v
API Response
   |
   | content_id + result + confidence_score + label + status
   v
User / Platform
```

### Appeal Flow

```text
Creator
   |
   | content_id + creator_id + appeal reason
   v
POST /appeal
   |
   | appeal request
   v
Appeal Handler
   |
   | content_id + appeal reason
   v
Status Update Component
   |
   | updated status: under review
   v
Audit Log
   |
   | saved appeal record
   v
API Response
   |
   | appeal_id + content_id + status + message
   v
Creator
```

## AI Tool Plan

- **Milestone 1:** Used AI to generate the initial Flask application skeleton and the `POST /submit` endpoint based on the planned API surface.
- **Milestone 2:** Used AI to generate the second detection signal and the confidence-scoring function using the detection signal descriptions and confidence thresholds from the planning document. The generated code was reviewed and adjusted so the scoring matched the thresholds defined in the specification.
- **Milestone 3:** Used AI to generate the transparency label function and the `POST /appeal` endpoint using the transparency label variants and appeals workflow described in the planning document. The generated code was modified to match the API contract and audit-log format.
- **Milestones 4 and 5:** Used AI to help refine the audit log, rate limiting, testing, and documentation while ensuring the implementation remained consistent with the planned architecture.
