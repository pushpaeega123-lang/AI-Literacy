"""
Assessment Bank module
- Defines learning levels and skills
- Provides scoring, weak-skill detection, recommendation mapping
- Generates a simple personalized learning plan

Usage:
    python scripts/assessment_bank.py

This is server-side logic and can be imported into `app.py` later.
"""
from typing import Dict, List, Tuple
import json

SKILLS = ["Reading", "Writing", "Listening", "Speaking", "Comprehension"]
LEVELS = ["Beginner", "Basic", "Intermediate", "Advanced"]

# Mapping of weak skill -> recommended activity templates (examples)
RECOMMENDATION_TEMPLATES = {
    "Reading": {
        "Beginner": ["Picture Reading", "Label Matching", "Letter Recognition"],
        "Basic": ["Word Reading", "Sight Words", "Picture Sentences"],
        "Intermediate": ["Paragraph Skimming", "Question-Answer Reading"],
        "Advanced": ["Critical Reading Exercises", "Inference Passages"]
    },
    "Writing": {
        "Beginner": ["Letter Tracing", "Trace Lines", "Drag Letters"],
        "Basic": ["Write Letter", "Write Short Words", "Fill-the-blanks"],
        "Intermediate": ["Write Sentences", "Construct Short Paragraphs"],
        "Advanced": ["Essay Practice", "Structured Writing Tasks"]
    },
    "Listening": {
        "Beginner": ["Alphabet Song", "Rhymes", "Identify Sounds"],
        "Basic": ["Single-word Audio", "Choose Picture by Audio"],
        "Intermediate": ["Short Story Questions"],
        "Advanced": ["Conversation Comprehension"]
    },
    "Speaking": {
        "Beginner": ["Say Animal Names", "Repeat Simple Words"],
        "Basic": ["Read Word Aloud", "Pronunciation Clips"],
        "Intermediate": ["Introduce Yourself", "Short Responses"],
        "Advanced": ["Describe Pictures", "Extended Speech Tasks"]
    },
    "Comprehension": {
        "Beginner": ["Picture Stories", "Identify Object/Action"],
        "Basic": ["Short Story Questions", "What/Who/Where"],
        "Intermediate": ["Paragraph Comprehension"],
        "Advanced": ["Multi-question Passage"]
    }
}

# Heuristics: lower score => higher priority. Threshold to consider weak skill.
WEAK_THRESHOLD = 50  # percent; skills <= threshold marked weak


def compute_skill_scores(responses: Dict[str, Dict[str, int]]) -> Dict[str, int]:
    """
    Compute skill scores from responses structure.
    Expected input format:
    {
      "Reading": {"correct": 3, "total": 5},
      "Writing": {"correct": 1, "total": 2},
      ...
    }
    Returns: { skill: percent_score }
    """
    scores = {}
    for skill in SKILLS:
        r = responses.get(skill, {})
        correct = r.get("correct", 0)
        total = r.get("total", 0)
        if total <= 0:
            percent = 0
        else:
            percent = int(round(100.0 * correct / total))
        scores[skill] = percent
    return scores


def detect_weak_skills(scores: Dict[str, int], threshold: int = WEAK_THRESHOLD) -> Tuple[List[str], List[str]]:
    """Return (weak_skills, strong_skills) based on threshold."""
    weak = [s for s, v in scores.items() if v <= threshold]
    strong = [s for s, v in scores.items() if v > threshold]
    return weak, strong


def map_recommendations(weak_skills: List[str], level: str) -> Dict[str, List[str]]:
    """Map each weak skill to recommended activities for given level."""
    recs = {}
    for skill in weak_skills:
        templates = RECOMMENDATION_TEMPLATES.get(skill, {})
        level_list = templates.get(level, []) if isinstance(templates, dict) else []
        # pick up to 3 activities
        recs[skill] = level_list[:3]
    return recs


def generate_personalized_plan(scores: Dict[str, int], level: str, max_items: int = 5) -> List[Dict]:
    """
    Produce an ordered plan of activities prioritizing weak skills.
    Each plan item: {title, skill, activity_type, estimated_duration_minutes}
    """
    weak, strong = detect_weak_skills(scores)
    # Build candidate activities: weak skills first (sorted by lowest score), then supportive activities
    sorted_weak = sorted(weak, key=lambda s: scores.get(s, 0))
    plan = []
    # Assign durations heuristically by level and activity type
    base_duration = {"Beginner": 5, "Basic": 8, "Intermediate": 12, "Advanced": 20}
    dur_base = base_duration.get(level, 10)
    for skill in sorted_weak:
        activities = RECOMMENDATION_TEMPLATES.get(skill, {}).get(level, [])
        for act in activities:
            item = {
                "title": act,
                "skill": skill,
                "activity_type": act,
                "estimated_duration_minutes": dur_base,
                "notes": f"Focus on {skill.lower()} practice for learners at {level} level",
            }
            plan.append(item)
            if len(plan) >= max_items:
                return plan
    # Fill remaining slots with supportive mixed-skill items
    mixed = [
        {"title": "Alphabet Song", "skill": "Listening", "activity_type": "Listening", "estimated_duration_minutes": 5},
        {"title": "Picture Reading", "skill": "Reading", "activity_type": "Reading", "estimated_duration_minutes": dur_base},
        {"title": "Letter Tracing", "skill": "Writing", "activity_type": "Writing", "estimated_duration_minutes": dur_base}
    ]
    i = 0
    while len(plan) < max_items and i < len(mixed):
        plan.append(mixed[i])
        i += 1
    return plan


def summarize_assessment(scores: Dict[str, int]) -> Dict:
    weak, strong = detect_weak_skills(scores)
    return {
        "scores": scores,
        "weak_skills": weak,
        "strong_skills": strong
    }


# Quick CLI smoke test
if __name__ == '__main__':
    # Example: beginner learner with mixed results
    example_responses = {
        "Reading": {"correct": 2, "total": 5},
        "Writing": {"correct": 1, "total": 4},
        "Listening": {"correct": 4, "total": 5},
        "Speaking": {"correct": 3, "total": 5},
        "Comprehension": {"correct": 1, "total": 5}
    }
    level = "Beginner"
    scores = compute_skill_scores(example_responses)
    summary = summarize_assessment(scores)
    recs = map_recommendations(summary["weak_skills"], level)
    plan = generate_personalized_plan(scores, level)
    out = {
        "summary": summary,
        "recommendations": recs,
        "personalized_plan": plan
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
