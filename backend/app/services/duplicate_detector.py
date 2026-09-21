import re
from typing import List, Dict

class DuplicateDetector:
    @staticmethod
    def _tokenize(text: str) -> set:
        words = re.findall(r'[a-zA-Z0-9]+', text.lower())
        stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'is', 'it', 'with', 'by', 'error', 'bug'}
        return {w for w in words if len(w) > 2 and w not in stopwords}

    @classmethod
    def calculate_similarity(cls, text1: str, text2: str) -> float:
        set1 = cls._tokenize(text1)
        set2 = cls._tokenize(text2)
        if not set1 or not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0

    @classmethod
    def find_potential_duplicates(cls, new_title: str, new_desc: str, existing_issues: List, threshold: float = 0.40) -> List[Dict]:
        new_text = f'{new_title} {new_desc}'
        duplicates = []
        for issue in existing_issues:
            existing_text = f'{issue.title} {issue.description}'
            sim = cls.calculate_similarity(new_text, existing_text)
            if sim >= threshold:
                duplicates.append({
                    'id': issue.id,
                    'issue_key': issue.issue_key,
                    'title': issue.title,
                    'dev_stage': issue.dev_stage,
                    'severity': issue.severity,
                    'similarity_percent': round(sim * 100, 1)
                })
        duplicates.sort(key=lambda x: x['similarity_percent'], reverse=True)
        return duplicates
