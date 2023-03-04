from django.db import models


class DialogueLine(models.Model):
    LOVED_GIFT = 'LOVED_GIFT'
    LIKED_GIFT = 'LIKED_GIFT'
    NEUTRAL_GIFT = 'NEUTRAL_GIFT'
    DISLIKED_GIFT = 'DISLIKED_GIFT'
    HATED_GIFT = 'HATED_GIFT'
    FIRST_MEETING = 'FIRST_MEETING'
    TALKED_TO = 'TALKED_TO'

    DIALOGUE_TRIGGERS = [
        (LOVED_GIFT, 'Loved Gift'),
        (LIKED_GIFT, 'Liked Gift'),
        (NEUTRAL_GIFT, 'Neutral Gift'),
        (DISLIKED_GIFT, 'Disliked Gift'),
        (HATED_GIFT, 'Hated Gift'),
        (FIRST_MEETING, 'First Meeting'),
        (TALKED_TO, 'Talked To'),
    ]

    speaker = models.ForeignKey('Villager', on_delete=models.CASCADE, related_name='dialogue_lines')
    affinity_tier = models.IntegerField(null=True, blank=True)
    trigger = models.CharField(max_length=13, choices=DIALOGUE_TRIGGERS, default=TALKED_TO)
    full_text = models.TextField()

    def __str__(self):
        return f'{self.speaker.name} says: {self.abbr_text}'

    def serialize(self):
        return {
            'name': self.speaker.name,
            'image_url': self.speaker.image_url,
            'full_text': self.full_text,
            'id': self.id,
        }

    @property
    def abbr_text(self):
        return f"{self.full_text[:50]}{'...' if len(self.full_text) > 50 else ''}"
