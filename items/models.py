from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
    STATUS_CHOICES = (
        ('lost', 'Lost'),
        ('found', 'Found'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='items')

    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    date = models.DateField()
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    image = models.ImageField(upload_to='items/', null=True, blank=True)

    def __str__(self):
        return self.title
    

class Claim(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE,related_name='claims')
    claimant = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')

    is_cleared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.claimant.username} → {self.item.title}"
    

# 🔥 Multiple Images Support (NEW)
class ClaimImage(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='claim_proofs/')

    def __str__(self):
        return f"Image for {self.claim.id}"
    

class Chat(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)