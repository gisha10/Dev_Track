from abc import ABC, abstractmethod
from datetime import datetime


VALID_STATUSES = ['open', 'in_progress', 'resolved', 'closed']
VALID_PRIORITIES = ['low', 'medium', 'high', 'critical']


class BaseEntity(ABC):
    @abstractmethod
    def validate(self):
        pass

    def to_dict(self):
        return {
            key: value
            for key, value in self.__dict__.items()
        }


class Reporter(BaseEntity):
    def __init__(self, id, name, email, team):
        self.id = id
        self.name = name
        self.email = email
        self.team = team

    def validate(self):
        if not self.name:
            raise ValueError('Name cannot be empty')
        if not self.email or '@' not in self.email:
            raise ValueError('Invalid email')
        if not self.team:
            raise ValueError('Team cannot be empty')


class Issue(BaseEntity):
    def __init__(self, id, title, description, status, priority, reporter_id):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.reporter_id = reporter_id
        self.created_at = str(datetime.now())

    def validate(self):
        if not self.title or not self.title.strip():
            raise ValueError('Title cannot be empty')
        if self.status not in VALID_STATUSES:
            raise ValueError('Invalid status. Allowed: ' + ', '.join(VALID_STATUSES))
        if self.priority not in VALID_PRIORITIES:
            raise ValueError('Invalid priority. Allowed: ' + ', '.join(VALID_PRIORITIES))

    def describe(self):
        return f"{self.title} [{self.priority}]"


class CriticalIssue(Issue):
    def describe(self):
        return f"[URGENT] {self.title} — needs immediate attention"


class LowPriorityIssue(Issue):
    def describe(self):
        return f"{self.title} — low priority, handle when free"
