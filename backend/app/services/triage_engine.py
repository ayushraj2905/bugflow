import re
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.project import BugCategory
from ..models.issue import Issue

class TriageEngine:
    SEVERITY_WEIGHTS = {
        'CRITICAL': 4,
        'MAJOR': 3,
        'MINOR': 2,
        'TRIVIAL': 1,
        'LOW': 1
    }

    CATEGORY_URGENCY_WEIGHTS = {
        'High Urgency': 3,
        'Medium Urgency': 2,
        'Low Urgency': 1,
        'High': 3,
        'Medium': 2,
        'Low': 1,
        'Critical': 3
    }

    KEYWORDS_CRITICAL = ['crash', 'data loss', 'exploit', 'security vulnerability', 'deadlock', 'fatal', 'kernel panic', 'unhandled exception in prod', 'vulnerability']
    KEYWORDS_MAJOR = ['timeout', '500 internal server', 'performance degradation', 'memory leak', 'broken payment', 'auth failure', 'database query error', 'infinite loop']
    KEYWORDS_MINOR = ['ui glitch', 'css', 'misaligned', 'spelling', 'formatting', 'button color', 'label text', 'responsive issue', 'typo']
    KEYWORDS_TRIVIAL = ['typo', 'color', 'spacing', 'alignment', 'font', 'padding']

    CATEGORY_MAPPING = {
        'Authentication & Security': ['auth', 'login', 'token', 'jwt', 'permission', 'forbidden', '401', '403', 'password', 'csrf', 'xss', 'security', 'vulnerability'],
        'Database & Performance': ['database', 'postgres', 'sql', 'query', 'slow', 'latency', 'pool', 'connection', 'deadlock', 'index', 'timeout'],
        'UI/UX & Frontend': ['css', 'button', 'modal', 'screen', 'responsive', 'layout', 'display', 'rendering', 'mobile', 'frontend', 'color', 'typo', 'alignment'],
        'API & Integrations': ['api', 'rest', 'endpoint', 'payload', 'webhook', 'json', 'http', 'status code', 'curl', 'header'],
        'CI/CD & DevOps': ['pipeline', 'docker', 'deploy', 'github', 'build', 'artifact', 'runner', 'environment', 'action']
    }

    CATEGORY_TO_URGENCY_TYPE = {
        'Authentication & Security': 'High Urgency',
        'Database & Performance': 'High Urgency',
        'API & Integrations': 'Medium Urgency',
        'CI/CD & DevOps': 'Medium Urgency',
        'UI/UX & Frontend': 'Low Urgency'
    }

    @classmethod
    def calculate_priority_score(cls, severity: str, category_name: str) -> Dict:
        sev_clean = (severity or 'MINOR').strip().upper()
        sev_weight = cls.SEVERITY_WEIGHTS.get(sev_clean, 2)

        # Map category name to urgency level
        urgency_type = cls.CATEGORY_TO_URGENCY_TYPE.get(category_name, 'Medium Urgency')
        urgency_weight = cls.CATEGORY_URGENCY_WEIGHTS.get(urgency_type, 2)

        # Priority Score = Severity Weight * Category Urgency Weight
        score = float(sev_weight * urgency_weight)

        # Final Priority Result:
        # Score >= 10 -> URGENT
        # Score 7 - 9 -> HIGH
        # Score 4 - 6 -> MEDIUM
        # Score < 4   -> LOW
        if score >= 10.0:
            priority_label = 'URGENT'
            action_badge = 'Drop everything and fix now!'
        elif score >= 7.0:
            priority_label = 'HIGH'
            action_badge = 'High priority resolution'
        elif score >= 4.0:
            priority_label = 'MEDIUM'
            action_badge = 'Normal sprint cycle'
        else:
            priority_label = 'LOW'
            action_badge = 'Low priority / when time permits'

        return {
            'severity': sev_clean,
            'severity_weight': sev_weight,
            'category_name': category_name,
            'urgency_type': urgency_type,
            'urgency_weight': urgency_weight,
            'priority_score': score,
            'priority_label': priority_label,
            'action_badge': action_badge,
            'formula': f'{sev_weight} (Severity) × {urgency_weight} ({urgency_type}) = {score}'
        }

    @classmethod
    def analyze_issue(cls, title: str, description: str, reproduction_steps: str = '', severity_override: str = None, category_override: str = None) -> Dict:
        combined = f'{title} {description} {reproduction_steps}'.lower()

        # Determine Severity if not overridden
        if severity_override and severity_override.upper() in cls.SEVERITY_WEIGHTS:
            severity = severity_override.upper()
        else:
            if any(k in combined for k in cls.KEYWORDS_CRITICAL):
                severity = 'CRITICAL'
            elif any(k in combined for k in cls.KEYWORDS_MAJOR):
                severity = 'MAJOR'
            elif any(k in combined for k in cls.KEYWORDS_TRIVIAL):
                severity = 'TRIVIAL'
            elif any(k in combined for k in cls.KEYWORDS_MINOR):
                severity = 'MINOR'
            else:
                severity = 'MINOR'

        # Determine Category if not overridden
        if category_override:
            matched_category = category_override
        else:
            matched_category = 'API & Integrations'
            max_matches = 0
            for cat_name, keywords in cls.CATEGORY_MAPPING.items():
                matches = sum(1 for k in keywords if k in combined)
                if matches > max_matches:
                    max_matches = matches
                    matched_category = cat_name

        # Calculate Priority using exact formula
        priority_calc = cls.calculate_priority_score(severity, matched_category)

        # Estimate effort (hours)
        effort_map = {'CRITICAL': 12.0, 'MAJOR': 8.0, 'MINOR': 4.0, 'TRIVIAL': 1.5, 'LOW': 2.0}
        estimated_effort = effort_map.get(severity, 4.0)

        return {
            'predicted_severity': severity,
            'predicted_category': matched_category,
            'predicted_priority': priority_calc['priority_label'],
            'priority_score': priority_calc['priority_score'],
            'priority_calculation': priority_calc,
            'estimated_effort': estimated_effort
        }

    @classmethod
    def recommend_developers(cls, issue_text: str, category_name: str, available_devs: List[User], db: Optional[Session] = None) -> List[Dict]:
        text = (issue_text + ' ' + category_name).lower()
        scored_devs = []

        for dev in available_devs:
            # 1. Base Score & Skill Match
            score = 50.0
            skills = [s.strip().lower() for s in (dev.core_skills or '').split(',')]

            matched_skills = [skill for skill in skills if skill in text or any(k in skill for k in text.split())]
            skill_hits = len(matched_skills)
            score += skill_hits * 15.0

            # 2. Proficiency bonus
            prof_bonus = {'Junior': 5, 'Mid': 15, 'Senior': 25, 'Lead': 30}
            score += prof_bonus.get(dev.proficiency, 10)

            # 3. Workload Check (Active Open Tasks)
            active_tasks_count = 0
            if db is not None:
                active_tasks_count = db.query(Issue).filter(
                    Issue.assignee_id == dev.id,
                    Issue.dev_stage != 'CLOSED'
                ).count()
            
            # Workload penalty: reduce score if developer already has many active tasks (don't overload)
            workload_penalty = min(25.0, active_tasks_count * 4.0)
            score -= workload_penalty

            # Cap final match percentage between 35% and 98%
            final_match = min(98.0, max(35.0, score))

            primary_skill_highlight = matched_skills[0].title() if matched_skills else ((dev.core_skills or 'General').split(',')[0].strip())
            task_label = f"{active_tasks_count} active task{'s' if active_tasks_count != 1 else ''}"
            summary_label = f"{dev.full_name} - {int(round(final_match))}% match ({primary_skill_highlight} expert, {task_label})"

            scored_devs.append({
                'dev_id': dev.id,
                'full_name': dev.full_name,
                'team': dev.team,
                'proficiency': dev.proficiency,
                'core_skills': dev.core_skills,
                'matched_skills': matched_skills,
                'active_tasks_count': active_tasks_count,
                'match_score': round(final_match, 1),
                'match_percent_int': int(round(final_match)),
                'summary_label': summary_label,
                'recommended_role': f'Primary Resolver ({dev.proficiency})'
            })

        scored_devs.sort(key=lambda x: x['match_score'], reverse=True)
        return scored_devs
