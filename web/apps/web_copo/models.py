from datetime import datetime, timedelta

import pytz
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_tools.middlewares.ThreadLocal import get_current_user
from web.settings.base import VIEWLOCK_TIMEOUT
from django.utils import timezone


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    orcid_id = models.TextField(max_length=40, blank=True)
    repo_manager = ArrayField(
        models.CharField(max_length=100, blank=True),
        blank=True,
        null=True,
    )
    repo_submitter = ArrayField(
        models.CharField(max_length=100, blank=True),
        blank=True,
        null=True,
    )

    # class Meta:
    # app_label = 'django.contrib.auth'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserDetails.objects.create(user=instance)
    try:
        ud = instance.userdetails
    except:
        UserDetails.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_details(sender, instance, **kwargs):
    instance.userdetails.save()


class Repository(models.Model):
    class Meta:
        managed = False  # No database table creation or deletion operations \
        # will be performed for this model.

        permissions = (
            ('customer_rigths', 'Global customer rights'),
            ('vendor_rights', 'Global vendor rights'),
            ('any_rights', 'Global any rights'),
        )


class test_model(models.Model):
    url = models.URLField()
    c = models.CharField(max_length=10, default="a")


class banner_view(models.Model):
    header_txt = models.TextField(max_length=100, blank=False, default="")
    body_txt = models.TextField(max_length=2000, blank=False, default="")
    active = models.BooleanField()


class ViewLock(models.Model):
    url = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timeLocked = models.DateTimeField()
    timeout = timedelta(seconds=300)

    def lockView(self, url):
        # method will throw error if lock already exists for url
        self.url = url
        self.user = get_current_user()
        self.timeLocked = datetime.utcnow()
        try:
            self.save()
            return True
        except ViewLock.MultipleObjectsReturned:
            return False

    def delete_self(self):
        self.delete()
        return True

    def unlockView(self, url):
        lock = ViewLock.objects.get(url=url)
        if lock:
            lock.delete()
            return True
        else:
            return False

    def isViewLockedCreate(self, url):
        # if this view is locked return True, if not, create lock and return False
        try:
            lock = ViewLock.objects.filter(url=url).get()
        except ViewLock.DoesNotExist as e:
            # view not locked
            self.lockView(url=url)
            return False
        if lock.user == get_current_user():
            # lock is owned by page requester, update timeLocked
            lock.timeLocked = datetime.utcnow()
            lock.save()
            return False
        else:
            if datetime.utcnow().replace(tzinfo=pytz.utc) - lock.timeLocked > self.timeout:
                # lock has expired
                lock.delete()
                self.lockView(url=url)
                return False
            else:
                # view is locked
                return True

    def remove_expired_locks(self):
        time_threshold = timezone.now() - VIEWLOCK_TIMEOUT
        locks = ViewLock.objects.filter(timeLocked__lte=time_threshold)
        for l in locks:
            l.delete()
        print(locks)
