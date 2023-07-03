from django.db import models
from accounts.models import *
from accounts.utils import *
# Create your models here.


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user')
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='userprofile')
    vendor_name = models.CharField(max_length=50)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.vendor_name
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            #update
            origin = Vendor.objects.get(pk=self.pk)
            if origin.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved
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
