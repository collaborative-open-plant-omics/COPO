# Created by fshaw at 25/06/2018

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from web.apps.web_copo.models import Repository


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Command to setup.sh COPO groups"

    # A command must define handle()
    def handle(self, *args, **options):
        self.stdout.write("Checking Groups")

        dm_group, created = Group.objects.get_or_create(name='data_managers')
        dtol_group, create = Group.objects.get_or_create(name='dtol_users')
        dtol_managers, created = Group.objects.get_or_create(name='dtol_sample_managers')
        dtol_notifiers, created = Group.objects.get_or_create(name='dtol_sample_notifiers')
        dtol_barcoders, created = Group.objects.get_or_create(name='dtol_barcoders')
        ct = ContentType.objects.get_for_model(Repository)

        Permission.objects.filter(codename="can_create_repo").delete()
        permission = Permission.objects.create(codename='can_create_repo',
                                               name='Can Create Repository',
                                               content_type=ct)
        dm_group.permissions.add(permission)
        Permission.objects.filter(codename="can_add_user_to_repo").delete()
        permission = Permission.objects.create(codename='can_add_user_to_repo',
                                           name='Can Add User to Repository',
                                           content_type=ct)
        dm_group.permissions.add(permission)
