# ai201-project4-provenance-guard

# Provenance Guard

## Detection Signals:

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

## Rate Limiter Evidence:

I gave the following command: curl -s -o /dev/null -w "%{http_code}\n" \
 -X POST http://127.0.0.1:5000/submit \
 -H "Content-Type: application/json" \
 -d '{"text":"This is a test submission for rate limit testing purposes only.","creator_id":"ratelimit-test"}'
And the result:
200
200
200
200
200
200
200
200
200
200
429
429

## Submission Test Results

### Submission 1 – AI-style Formal Writing

**Input**

> "Artificial intelligence represents a transformative paradigm shift in modern society.
> It is important to note that while the benefits of AI are numerous, it is equally
> essential to consider the ethical implications. Furthermore, stakeholders across various sectors must collaborate to ensure responsible deployment"

**Result**
```json
[
{
"attribution": "uncertain",
"confidence_score": 0.36,
"content_id": "77c08628-35df-4e44-9fd1-143806cfb8f9",
"creator_id": "test-user-1",
"label": "Uncertain label: This text has mixed signals. We cannot confidently determine whether it was human-written or AI-generated. Confidence score: 0.36.",
"signals": {
"signal_1": {
"name": "Repetition / Generic Pattern Score",
"score": 0.12
},
"signal_2": {
"name": "Sentence Variation / Burstiness Score",
"score": 0.6
}
},
"status": "classified"
}
]

---

### Submission 2 – Casual Human Writing

**Input**

> "ok so i finally tried that new ramen place downtown and honestly?
> underwhelming. the broth was fine but they put WAY too much sodium in it and
> i was thirsty for like three hours after. my friend got the spicy version and
> said it was better. probably won't go back unless someone drags me there"

**Result**

{
"attribution": "likely_human",
"confidence_score": 0.3,
"content_id": "9599cd38-d7b5-44cb-b494-da409657f16d",
"creator_id": "test-user-1",
"label": "High-confidence human label: This text shows strong patterns associated with human-written work. Confidence score: 0.3.",
"signals": {
"signal_1": {
"name": "Repetition / Generic Pattern Score",
"score": 0.0
},
"signal_2": {
"name": "Sentence Variation / Burstiness Score",
"score": 0.6
}
},
"status": "classified"
}

---

### Submission 3 – Formal Academic Writing

**Input**

> "The relationship between monetary policy and asset price inflation has been
> extensively studied in the literature. Central banks face a fundamental tension
> between their mandate for price stability and the unintended consequences of
> prolonged low interest rates on equity and real estate valuations."

**Result**

{
"attribution": "uncertain",
"confidence_score": 0.49,
"content_id": "75d64576-023f-43f4-a3cc-d74af5d5c801",
"creator_id": "test-user-1",
"label": "Uncertain label: This text has mixed signals. We cannot confidently determine whether it was human-written or AI-generated. Confidence score: 0.49.",
"signals": {
"signal_1": {
"name": "Repetition / Generic Pattern Score",
"score": 0.14
},
"signal_2": {
"name": "Sentence Variation / Burstiness Score",
"score": 0.85
}
},
"status": "classified"
}

---

### Submission 4 – Borderline Writing

**Input**

> "I've been thinking a lot about remote work lately. There are genuine tradeoffs —
> flexibility and no commute on one side, isolation and blurred work-life boundaries
> on the other. Studies show productivity varies widely by individual and role type."

**Result**
"attribution": "uncertain",
"confidence_score": 0.46,
"content_id": "596def25-aff9-466d-a74d-f9ff96d08511",
"creator_id": "test-user-1",
"label": "Uncertain label: This text has mixed signals. We cannot confidently determine whether it was human-written or AI-generated. Confidence score: 0.46.",
"signals": {
"signal_1": {
"name": "Repetition / Generic Pattern Score",
"score": 0.08
},
"signal_2": {
"name": "Sentence Variation / Burstiness Score",
"score": 0.85
}
},
"status": "classified"

### Submission 5 –Likely AI

**Input**

Artificial intelligence is important. Artificial intelligence is important for society. Artificial intelligence is important for education. Artificial intelligence is important for business. Artificial intelligence is important for healthcare. Artificial intelligence is important for research. Artificial intelligence is important for innovation. Artificial intelligence is important for the future.

**Result**

{
"attribution": "likely_ai",
"confidence_score": 0.77,
"content_id": "6fd3e03c-e761-4654-abe6-f32e4116d081",
"creator_id": "test-user-1",
"label": "High-confidence AI label: This text shows strong patterns associated with AI-generated writing. Confidence score: 0.77.",
"signals": {
"signal_1": {
"name": "Repetition / Generic Pattern Score",
"score": 0.7
},
"signal_2": {
"name": "Sentence Variation / Burstiness Score",
"score": 0.85
}
},
"status": "classified"
}

## Observations

- Casual writing produced the lowest confidence score and was classified as **Likely Human**.
- Formal and polished writing produced higher Signal 2 scores because the sentence structure was more consistent.

## Audit log json report results:
## Audit Log Sample

```json
[
  {
    "content_id": "9599cd38-d7b5-44cb-b494-da409657f16d",
    "creator_id": "test-user-1",
    "timestamp": "2026-06-29T20:33:24.324469+00:00",
    "attribution": "likely_human",
    "confidence": 0.30,
    "signal_1_score": 0.00,
    "signal_1_name": "Repetition / Generic Pattern Score",
    "signal_2_score": 0.60,
    "signal_2_name": "Sentence Variation / Burstiness Score",
    "status": "classified"
  },
  {
    "content_id": "6fd3e03c-e761-4654-abe6-f32e4116d081",
    "creator_id": "test-user-1",
    "timestamp": "2026-06-29T20:36:26.566024+00:00",
    "attribution": "likely_ai",
    "confidence": 0.77,
    "signal_1_score": 0.70,
    "signal_1_name": "Repetition / Generic Pattern Score",
    "signal_2_score": 0.85,
    "signal_2_name": "Sentence Variation / Burstiness Score",
    "status": "classified"
  },
  {
    "event_type": "appeal",
    "appeal_id": "205a44b8-bde4-4e2b-8d33-5b78395a6e1e",
    "content_id": "6fd3e03c-e761-4654-abe6-f32e4116d081",
    "creator_id": "test-user-1",
    "appeal_reasoning": "I wrote this myself from personal experience. My writing style is naturally formal.",
    "timestamp": "2026-06-29T20:52:26.086588+00:00",
    "status": "under_review"
  }
]
```
## What needs to be changed before production?

I would definitely add more detection signals, and I would use advanced machine learning techniques instead of simple heuristics. I would have need to test on larger evaluation dataset.

## Known Limitations:

I would say I need to test with more data and data types such as poems, speeches, academic writing and
edited AI text. I also would need to increase the signal types. Also poetry may be misclassified because repetition is often intentional in poetry, so Signal 1 may treat human poetic repetition as AI-like.

## Spec Reflection:

Planning ahead made the implementation much easier because I had already defined the architecture and the responsibilities of each component. I didn't feel lost while coding since I knew how the submission flow, detection signals, confidence scoring, transparency labels, and appeals workflow fit together. Without planning first, it would have been easy to confuse concepts such as detection signals, confidence scores, and transparency labels. Designing the system before implementing it gave me a much clearer understanding of how each part should work together

## AI Usage:

I asked AI to generate the Flask skeleton. It produced a basic /submit route, and I revised it to include creator_id, content_id, structured signal scores, and audit logging.

## Appeal example from audit:

This audit log entry shows that the appeal was recorded alongside the original classification and that the content status was updated to under_review.

curl -X POST http://127.0.0.1:5000/appeal \
 -H "Content-Type: application/json" \
 -d '{
"content_id":"6fd3e03c-e761-4654-abe6-f32e4116d081",
"creator_id":"test-user-1",
"creator_reasoning":"I wrote this myself from personal experience. My writing style is naturally formal."
}'
{
"appeal_id": "205a44b8-bde4-4e2b-8d33-5b78395a6e1e",
"content_id": "6fd3e03c-e761-4654-abe6-f32e4116d081",
"creator_id": "test-user-1",
"message": "Your appeal has been received and the content is now under review.",
"status": "under_review"
}

## AI Usage

### Example 1: Flask Application Skeleton

I asked the AI tool to generate a Flask application skeleton with a `POST /submit` endpoint based on my API design and architecture diagram. The generated code included a basic route and request handling. I revised the code by adding `creator_id`, `content_id`, structured signal scores, audit logging, and validation to match my project specification.

### Example 2: Confidence Scoring and Appeals Workflow

I asked the AI tool to generate the second detection signal, confidence-scoring logic, transparency label function, and the `POST /appeal` endpoint using my planning document as input. The generated implementation was modified by changing the confidence thresholds to match my specification, updating the appeal endpoint to use the `creator_reasoning` field, changing the status to `under_review`, and ensuring appeals were recorded correctly in the audit log.
