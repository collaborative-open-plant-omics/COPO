from django.test import SimpleTestCase
from web.apps.web_copo.utils.group_functions import get_group_membership_asString
from django_tools.middlewares import ThreadLocal

class UtilsTest(SimpleTestCase):
    def test_user_group_membership(self):
        print(ThreadLocal.get_current_request())
        print(ThreadLocal.get_current_request().user.groups.all())
        # print(get_group_membership_asString)
        # assert "dtol_sample_managers" in get_group_membership_asString
        self.assertTrue(get_group_membership_asString, "dtol_sample_managers")
    # dtol_sample_managers
# erga_sample_managers
