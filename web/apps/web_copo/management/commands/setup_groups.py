# Created by fshaw at 25/06/2018

from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from web.apps.web_copo.models import Repository


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Command to setup.sh COPO groups"

    # A command must define handle()
    def handle(self, *args, **options):
        self.stdout.write("Checking Groups")

        # group for creating custom repos
        dm_group, created = Group.objects.get_or_create(name='data_managers')

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

        # view dtol functionality
        dtol_group, create = Group.objects.get_or_create(name='dtol_users')
        # view dtol accept/reject view
        dtol_managers, created = Group.objects.get_or_create(name='dtol_sample_managers')
        # receive dtol notification emails
        dtol_notifiers, created = Group.objects.get_or_create(name='dtol_sample_notifiers')
        # view erga functionality
        erga_group, create = Group.objects.get_or_create(name='erga_users')
        # view erga accept/reject view
        erga_managers, created = Group.objects.get_or_create(name='erga_sample_managers')
        # receive erga notification emails
        erga_notifiers, created = Group.objects.get_or_create(name='erga_sample_notifiers')
        # view dtol env functionality
        dtolenv_group, create = Group.objects.get_or_create(name='dtolenv_users')
