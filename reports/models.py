from django.db import models

class EmployeeScore(models.Model):
    name = models.CharField(max_length=100)
    absent_value = models.IntegerField()
    late_value = models.IntegerField()
    referral_value = models.IntegerField()
    visitors_value = models.IntegerField()
    TYFCB_value = models.IntegerField()
    training_value = models.IntegerField()
    testimonial_value = models.IntegerField()

    def __str__(self):
        return self.name

class MemberTrainingReport(models.Model):
    member_name = models.CharField(max_length=100)
    training_attended = models.IntegerField()

    def __str__(self):
        return self.member_name


