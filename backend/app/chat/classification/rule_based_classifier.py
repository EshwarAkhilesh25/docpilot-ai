"""Rule-based intent classifier using regex patterns."""

import re

from app.chat.interfaces.intent_classifier import IntentClassifier


class RuleBasedClassifier(IntentClassifier):
    """Classifies intent using a set of predefined regex patterns."""

    def __init__(self):
        # Ordered by priority
        self.patterns = [
            (r"(?i)\b(summarize|summary|tl;dr|tldr)\b", "SUMMARIZE"),
            (r"(?i)\b(compare|differences|similarities)\b", "COMPARE"),
            (r"(?i)\b(mcq|multiple choice|quiz)\b", "MCQ"),
            (r"(?i)\b(flashcard|flash cards)\b", "FLASHCARDS"),
            (r"(?i)\b(key findings|main points|takeaways)\b", "KEY_FINDINGS"),
            (r"(?i)\b(explain|what is|how does)\b", "EXPLAIN"),
            (r"(?i)\b(timeline|chronological|dates)\b", "TIMELINE"),
            (r"(?i)\b(action items|tasks|next steps)\b", "ACTION_ITEMS"),
        ]

    async def classify(self, question: str) -> str:
        """Classify the question using regex patterns. Defaults to GENERAL_QA."""
        for pattern, intent in self.patterns:
            if re.search(pattern, question):
                return intent
        return "GENERAL_QA"
