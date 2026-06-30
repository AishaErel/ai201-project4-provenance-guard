
from flask import Flask, request, jsonify
from datetime import datetime, timezone
import uuid
import json
import os  # checks if the log file exists
import re
import statistics
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Flask creates a web app
# request reads incoming data from the user
# jsonify sends JSON responses back

app = Flask(__name__)  # create the flask app
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

LOG_FILE = "audit_log.json"  # log file will be stored here


def repetition_generic_pattern_score(text):
    # this function checks how repetitive the text is

    words = text.lower().split()  # make the text lowercase and split it into words

    if not words:
        return 0.0

    unique_words = set(words)

    # compares unique words to total words
    # if many words repeat, the score gets higher
    score = 1 - (len(unique_words) / len(words))

    return round(max(0.0, min(1.0, score)), 2)


def sentence_variation_score(text):
    # this function checks how much sentence lengths vary

    # split the text into sentences
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # if there are fewer than 2 sentences,
    # return a neutral score
    if len(sentences) < 2:
        return 0.5

    # count the number of words in each sentence
    sentence_lengths = [len(sentence.split()) for sentence in sentences]

    average_length = sum(sentence_lengths) / len(sentence_lengths)
    variance = statistics.pvariance(sentence_lengths)

    if average_length == 0:
        return 0.5

    variation_ratio = variance / average_length

    # Low variation means the writing is very even/uniform,
    # which we treat as more AI-like.
    if variation_ratio < 2:
        return 0.85
    elif variation_ratio < 5:
        return 0.60
    elif variation_ratio < 10:
        return 0.40
    else:
        return 0.20


def calculate_confidence(signal1_score, signal2_score):
    # combine both signals into one confidence score
    return round((signal1_score + signal2_score) / 2, 2)


def get_final_attribution(confidence_score):
    # convert the combined confidence score into one final label

    if confidence_score >= 0.70:
        return "likely_ai"
    elif confidence_score <= 0.35:
        return "likely_human"
    else:
        return "uncertain"


def generate_label(attribution, confidence_score):
    if attribution == "likely_ai":
        return (
            "High-confidence AI label: This text shows strong patterns "
            f"associated with AI-generated writing. Confidence score: {confidence_score}."
        )

    if attribution == "likely_human":
        return (
            "High-confidence human label: This text shows strong patterns "
            f"associated with human-written work. Confidence score: {confidence_score}."
        )

    return (
        "Uncertain label: This text has mixed signals. We cannot confidently "
        f"determine whether it was human-written or AI-generated. Confidence score: {confidence_score}."
    )


def get_log():
    # reads the audit log

    # if the file does not exist, return empty
    if not os.path.exists(LOG_FILE):
        return []

    # if file exists, it opens it and loads the saved entries
    with open(LOG_FILE, "r") as file:
        return json.load(file)


def save_log_entry(entry):
    # saves one new log entry

    entries = get_log()
    entries.append(entry)

    # it writes the updated list back into audit_log.json
    with open(LOG_FILE, "w") as file:
        json.dump(entries, file, indent=2)

def test_signals():
    test_inputs = [
        {
            "name": "Clearly AI-generated",
            "text": "Artificial intelligence represents a transformative paradigm shift in modern society. It is important to note that while the benefits of AI are numerous, it is equally essential to consider the ethical implications. Furthermore, stakeholders across various sectors must collaborate to ensure responsible deployment."
        },
        {
            "name": "Clearly human-written",
            "text": "ok so i finally tried that new ramen place downtown and honestly? underwhelming. the broth was fine but they put WAY too much sodium in it and i was thirsty for like three hours after. my friend got the spicy version and said it was better. probably won't go back unless someone drags me there"
        },
        {
            "name": "Borderline formal human writing",
            "text": "The relationship between monetary policy and asset price inflation has been extensively studied in the literature. Central banks face a fundamental tension between their mandate for price stability and the unintended consequences of prolonged low interest rates on equity and real estate valuations."
        },
        {
            "name": "Borderline lightly edited AI output",
            "text": "I've been thinking a lot about remote work lately. There are genuine tradeoffs — flexibility and no commute on one side, isolation and blurred work-life boundaries on the other. Studies show productivity varies widely by individual and role type."
        }
    ]

    for item in test_inputs:
        signal1 = repetition_generic_pattern_score(item["text"])
        signal2 = sentence_variation_score(item["text"])
        confidence = calculate_confidence(signal1, signal2)
        attribution = get_final_attribution(confidence)

        print(item["name"])
        print("Signal 1:", signal1)
        print("Signal 2:", signal2)
        print("Confidence:", confidence)
        print("Attribution:", attribution)
        print()
# this creates the POST /submit route,
# where users submit their text


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")
def submit():

    # this reads the JSON body from the request
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    # data sent was successful
    # pull out the submitted text and creator ID
    text = data.get("text")
    creator_id = data.get("creator_id")

    if not text or not creator_id:
        return jsonify({"error": "text and creator_id are required"}), 400

    # this creates a unique ID for this submission
    content_id = str(uuid.uuid4())

    # run Signal 1
    signal1_score = repetition_generic_pattern_score(text)

    # run Signal 2
    signal2_score = sentence_variation_score(text)

    # combine both signals into one confidence score
    confidence_score = calculate_confidence(
        signal1_score,
        signal2_score
    )

    # convert the combined score into one final attribution
    attribution = get_final_attribution(confidence_score)

    # create the transparency label
    label = generate_label(attribution, confidence_score)

    # create one structured audit log entry
    log_entry = {
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attribution": attribution,
        "confidence": confidence_score,
        "signal_1_score": signal1_score,
        "signal_1_name": "Repetition / Generic Pattern Score",
        "signal_2_score": signal2_score,
        "signal_2_name": "Sentence Variation / Burstiness Score",
        "status": "classified"
    }
    

    # save the audit log
    save_log_entry(log_entry)

    # response returned to the user
    response = {
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": attribution,
        "signals": {
            "signal_1": {
                "name": "Repetition / Generic Pattern Score",
                "score": signal1_score
            },
            "signal_2": {
                "name": "Sentence Variation / Burstiness Score",
                "score": signal2_score
            }
        },
        "confidence_score": confidence_score,
        "label": label,
        "status": "classified"
    }

    return jsonify(response), 200
@app.route("/appeal", methods=["POST"]) #users may appeal the decision
def appeal():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    content_id = data.get("content_id")
    creator_id = data.get("creator_id")
    creator_reasoning = data.get("creator_reasoning")

    if not content_id or not creator_id or not creator_reasoning:
       return jsonify({"error": "content_id, creator_id, and creator_reasoning are required"}), 400

    #create a unique appeal id
    appeal_id = str(uuid.uuid4())

    log_entry = {
        "event_type": "appeal",
        "appeal_id": appeal_id,
        "content_id": content_id,
        "creator_id": creator_id,
        "appeal_reasoning": creator_reasoning,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "under_review"
    }

    save_log_entry(log_entry)

    response = {
        "appeal_id": appeal_id,
        "content_id": content_id,
        "creator_id": creator_id,
        "status": "under_review",
        "message": "Your appeal has been received and the content is now under review."
    }

    return jsonify(response), 200

@app.route("/log", methods=["GET"])
def log():
    return jsonify({"entries": get_log()}), 200


if __name__ == "__main__":
    app.run(debug=True)

