""" module generates social accounts """
__author__ = 'etuka'

from django.core.management.base import BaseCommand

import psycopg2
from tools import resolve_env


class Command(BaseCommand):
    help = 'Generate social accounts'

    def handle(self, *args, **options):
        db_host = resolve_env.get_env('POSTGRES_SERVICE')
        db_name = resolve_env.get_env('POSTGRES_DB')
        db_user = resolve_env.get_env('POSTGRES_USER')
        db_pass = resolve_env.get_env('POSTGRES_PASSWORD')
        db_port = resolve_env.get_env('POSTGRES_PORT')

        conn_string = "dbname=%s user=%s password=%s host=%s port=%s" % (
            db_name, db_user, db_pass, db_host, db_port)

        try:
            print("Connecting to database...")
            conn = psycopg2.connect(conn_string)

            cursor = conn.cursor()
            print("Connected!\n")
        except (Exception, psycopg2.DatabaseError) as error:
            self.stdout.write(self.style.ERROR("Encountered error while creating social accounts: " + str(error)))
            raise

        # clear target tables preparatory for new data
        try:
            print("Deleting from target tables...\n")
            cursor.execute("DELETE FROM socialaccount_socialapp_sites")
            cursor.execute("DELETE FROM django_site")
            cursor.execute("DELETE FROM socialaccount_socialapp")
        except (Exception, psycopg2.DatabaseError) as error:
            self.stdout.write(self.style.ERROR("Encountered error while creating social accounts: " + str(error)))
            raise

        try:
            cursor.execute("INSERT INTO django_site (id, domain, name) VALUES (%s, %s, %s)",
                           (1, "www.copo-project.org", "www.copo-project.org"))

            ORCID_CLIENT_ID = resolve_env.get_env('ORCID_CLIENT')
            ORCID_SECRET = resolve_env.get_env('ORCID_SECRET')
            FACEBOOK_SECRET = resolve_env.get_env('FACEBOOK_SECRET')
            TWITTER_SECRET = resolve_env.get_env('TWITTER_SECRET')
            GOOGLE_SECRET = resolve_env.get_env('GOOGLE_SECRET')
            

            cursor.execute(
                "INSERT INTO socialaccount_socialapp (id, provider, name, client_id, secret, key) VALUES (%s, %s, %s, %s, %s, %s)",
                (1, "google", "Google", "197718904608-mubhgir39dr8e159ef4hb3l5i8me71b6.apps.googleusercontent.com",
                 GOOGLE_SECRET, " "))
            cursor.execute(
                "INSERT INTO socialaccount_socialapp (id, provider, name, client_id, secret, key) VALUES (%s, %s, %s, %s, %s, %s)",
                (2, "orcid", "Orcid", ORCID_CLIENT_ID, ORCID_SECRET, " "))
            cursor.execute(
                "INSERT INTO socialaccount_socialapp (id, provider, name, client_id, secret, key) VALUES (%s, %s, %s, %s, %s, %s)",
                (3, "facebook", "Facebook", "497282503814650", FACEBOOK_SECRET, " "))
            cursor.execute(
                "INSERT INTO socialaccount_socialapp (id, provider, name, client_id, secret, key) VALUES (%s, %s, %s, %s, %s, %s)",
                (4, "twitter", "Twitter", "qrwJCJG9aBngGnBKrnvwgGNYc", TWITTER_SECRET, " "))

            print("Creating 'socialaccount_socialapp_sites' record...\n")
            cursor.execute("INSERT INTO socialaccount_socialapp_sites (id, socialapp_id, site_id) VALUES (%s, %s, %s)",
                           (1, 1, 1))
            cursor.execute("INSERT INTO socialaccount_socialapp_sites (id, socialapp_id, site_id) VALUES (%s, %s, %s)",
                           (2, 2, 1))
            cursor.execute("INSERT INTO socialaccount_socialapp_sites (id, socialapp_id, site_id) VALUES (%s, %s, %s)",
                           (3, 3, 1))
            cursor.execute("INSERT INTO socialaccount_socialapp_sites (id, socialapp_id, site_id) VALUES (%s, %s, %s)",
                           (4, 4, 1))

            self.stdout.write(self.style.SUCCESS('Successfully created social accounts'))
        except (Exception, psycopg2.DatabaseError) as error:
            self.stdout.write(self.style.ERROR("Encountered error while creating social accounts: " + str(error)))
            raise

        # commit and close connection
        conn.commit()
        cursor.close()
        conn.close()
