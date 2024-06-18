from django.db import models
from accounts.models import *
from accounts.utils import *
from datetime import time, datetime, date
# Create your models here.


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user')
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='userprofile')
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.vendor_name
    
    # for it to have a database for is_open or is_closed
    def is_open(self):
        # Check current day's opening hours
        today_date = date.today()
        today = today_date.isoweekday() # this returns the numerical value of the day of the week just like in the model
        
        current_opening_hours = Opening_hour.objects.filter(vendor=self, day=today)
        now = datetime.now()
        current_time = now.strftime('%H:%M:%S')
        is_open = None
        for i in current_opening_hours:
            if not i.is_closed:
                start = str(datetime.strptime(i.from_hour, '%I:%M %p').time())
                end = str(datetime.strptime(i.to_hour, '%I:%M %p').time())
                
                if current_time > start and current_time < end:
                    is_open = True
                    break
                else:
                    is_open = False
        return is_open
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            #update
            origin = Vendor.objects.get(pk=self.pk)
            if origin.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                    'to_email': self.user.email,
                }
                if self.is_approved == True:
                    #Send notification email
                    mail_subject = "Congratulations! Your Restaurant has been Approved By FoodieHub Team"
                    send_notification(mail_subject, mail_template, context)
                else:
                    #send notification email
                    mail_subject = "We're sorry! Your Restaurant is not Eligible to be Published on the Marketplace, Please contact support@foodiehub.com"
                    send_notification(mail_subject, mail_template, context)
        return super(Vendor, self).save(*args, **kwargs)

DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("saturday")),
    (7, ("Sunday")),
]

HOUR_OF_DAY_24 = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0, 24) for m in (0, 30)]
class Opening_hour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour') # This makes sure you don't duplicate day and time
    
    def __str__(self):
        return self.get_day_display() #get_{field name}_display is an inbuilt function, field name stands for the model field