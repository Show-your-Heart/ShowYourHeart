import logging
from dataclasses import dataclass
from enum import Enum

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils.translation import gettext as _
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from apps.demo.models import Data
from apps.users.models import User

logging.basicConfig(level=logging.INFO)


@dataclass
class SampleUser:
    name: str
    surnames: str
    email: str
    password: str
    email_verification_code: str


class Strings(Enum):
    """
    Collect all the strings that you plan to use to find elements in the code
    that are susceptible to translation here.
    That way it will be easier to maintain the right version of the string
    whenever some text is changed.

    Also, during development we might only have english versions of the strings,
    but when applying the translations, all of them will need to be updated
    here.

    # IMPORTANT, ABOUT TRANSLATIONS:
    If you assert strings, i.e. like this:
        assert Strings.ADMIN_TITLE.value == self.selenium.title
    You need to be using 'gettext', NOT gettext_lazy.

    If for some reason you need to switch to gettext_lazy, these assertions will
    fail. In this case you should change all the assertions to something like
    this:
        assert str(Strings.ADMIN_TITLE.value) == self.selenium.title

    That way, the str() will force the resolution of the translation, instead of
    sending an object.

    """

    MENU_ADMIN = _("Administration panel")
    ADMIN_TITLE = _("Site administration | Django site admin")
    LOGOUT = _("Log out")
    SIGNUP_TITLE = _("%s | Create an account") % settings.PROJECT_NAME
    PROFILE_TITLE = _("%s | Profile details") % settings.PROJECT_NAME
    REGISTRY_UPDATE_TITLE = _("%s | Registry updated") % settings.PROJECT_NAME
    PASSWORD_CHANGE_TITLE = _("%s | Password change") % settings.PROJECT_NAME
    EMAIL_VALIDATION_TITLE = _("%s | Mail validation") % settings.PROJECT_NAME
    DEMO_TITLE = _("%s | Demo") % settings.PROJECT_NAME
    DEMO_CREATE = _("%s | Demo Create") % settings.PROJECT_NAME
    DEMO_DETAILS = _("%s | Demo Details") % settings.PROJECT_NAME
    DEMO_UPDATE = _("%s | Demo Update") % settings.PROJECT_NAME


@override_settings(
    ALLOWED_HOSTS=["*"],
    STORAGES={
        "default": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
    POST_OFFICE={
        "BACKENDS": {
            "default": "django.core.mail.backends.locmem.EmailBackend",
        },
        "DEFAULT_PRIORITY": "now",
    },
)
class MySeleniumTests(StaticLiveServerTestCase):
    """
    STATICFILES_STORAGE + StaticLiveServerTestCase vs LiveServerTestCase:
    Just using LiveServerTestCase it will not work because the tests run with
    debug disabled, meaning that it will trigger Whitenoise's static files
    indexation.
    For that to work, the static files need to be there, therefore, the tests
    will only work if you run `collectstatic` before running the tests.

    We can avoid Whitenoise to crash by overriding the setting STATICFILES_STORAGE
    to the default that Django uses.

    But then, Django will still try to serve the static files, so we need to
    extend StaticLiveServerTestCase because this class overrides the static
    serving behaviour to do the same that it does with DEBUG enabled - that is,
    to serve the files without any need to `collectstatic` first.
    """

    host = settings.APP_HOST_NAME
    # Uncomment this code if you want Selenium to connect to the actual web
    # service instead of the test one. Is assuming that Gunicorn is starting
    # it at the port 8000, because you have to use the internal port and
    # not the one that Docker is exposing outside.
    #
    # Beware that Selenium will be using the database in the state that you
    # have it now, but those tests are designed to work only with a fresh
    # database, and also that the override_settings is only affecting the test
    # server that you will not be using.
    # live_server_url = 'http://{}:8000'.format(
    #     socket.gethostbyname(socket.gethostname())
    # )
    obj_user1 = None
    obj_user2 = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up the Selenium WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")  # Disable sandboxing for Docker
        cls.selenium = webdriver.Remote(
            command_executor=f"http://{settings.SELENIUM_HOST_NAME}:4444/wd/hub",
            options=options,
        )
        cls.selenium.implicitly_wait(10)  # Set implicit wait time
        cls.sample_data = {
            "first_user": SampleUser(
                name="Andrew",
                surnames="McTest",
                email="andrew@codi.coop",
                password="0pl#9okm8ijn",
                email_verification_code="1234",
            ),
        }

    @classmethod
    def tearDownClass(cls):
        # Close the Selenium WebDriver
        cls.selenium.quit()
        super().tearDownClass()

    def reverse_absolute_url(self, reverse_string):
        return self.absolute_url_of_path(reverse(reverse_string))

    def absolute_url_of_path(self, path):
        return f"{self.live_server_url}{path}"

    def burger_menu_action(self):
        burger_menu = self.selenium.find_element(
            By.ID,
            "burger_button",
        )
        burger_menu.click()

    def logging_url_title_and_assert_title(self, title=None):
        logging.info(f"Opened: {self.selenium.current_url}")
        logging.info(f"Title: {self.selenium.title}")
        assert title == self.selenium.title

    def _check_mail_sent(self, recipient, string_in_body=""):
        """
        During the test, every time an email is sent it gets added to
        mail.outbox.
        This makes it difficult to test whether a specific email is sent or not.

        Instructions to test the emails

        If there's 1 email sent and pending to be tested:
        - Call this method normally.
        - After that, the email will be removed from the outbox, so you cannot
        test it a second time.

        If there's more than 1 email:
        - Call this method as many times as emails are pending to be tested.
        - In each call, the email in the index 0 of the outbox will be tested
        and removed from the outbox. So the different calls to this method will
        need to be done in the same order as the emails were sent.
        """
        self.assertGreaterEqual(len(mail.outbox), 1)
        current_mail = mail.outbox.pop(0)
        # The mail's "to" property is a list, as it can be sent to multiple
        # recipients at once. We are only testing for one.
        self.assertIn(recipient, current_mail.to)
        logging.info(f"Checked: Sent email to {recipient}")
        self.assertIn(string_in_body, current_mail.body)
        logging.info(f'Checked: "{string_in_body}" present in email body')

    def click_non_interactable_element(self, element):
        # Checkboxes are not rendered as is, but hidden by CSS and replaced with
        # other elements, with the purpose of styling them better.
        # Because of that, you cannot send a click() or interact with the
        # checkbox directly from Selenium; it'll throw the error:
        # selenium.common.exceptions.ElementNotInteractableException: Message:
        # element not interactable
        # The simplest solution is to send the click via JS:
        self.selenium.execute_script("arguments[0].click();", element)

    def select_element_by_text(self, text):
        """
        Select an element by its text
        """
        elements = self.selenium.find_elements(
            By.XPATH,
            f"//*[contains(text(), '{text}')]",
        )
        return elements[0] if elements else None

    def test_selenium(self):
        """
        Selenium tests controller

        We need the Selenium flow to follow a specific order, because each action
        will probably depend on the data and changes produced by previous ones.

        If we do that in different tests, we cannot ensure this order and also
        the principle is to make tests that are standalone.

        Because of that, we're using a single test method and splitting it
        in other private methods to make it more organized.
        """

        # Preparations
        self._resize()

        # Fer login amb el compte d'admin que crea per defecte.
        # Verifica que al menú de l'app apareix el botó per anar a l'admin.
        self._admin_login()
        logging.info("Test Login finished.")

        # Crea un nou usuari.
        # Verifica que al menú de l'app apareix el botó per crear un usuari new.
        self._signup()
        logging.info("Test Signup finished.")

        self._verify_email()
        logging.info("Test Verify email finished.")

        self._update_profile()
        logging.info("Test Update profile finished.")

        self._password_change()
        logging.info("Test Password change finished.")

        self._home()
        logging.info("Test Home finished.")

        self._demo_list()
        logging.info("Test Demo List finished.")

        self._demo_create()
        logging.info("Test Demo Create finished.")

        self._demo_details()
        logging.info("Test Demo Details finished.")

        self._demo_update()
        logging.info("Test Demo Update finished.")

        logging.info("#####################################")
        logging.info("#### All tests Selenium finished ####")
        logging.info("#####################################")

    def _resize(self):
        """
        Elements need to be in viewport to be interactable.
        For instance, we cannot send a click() to a checkbox if it's not
        visible, so we either resize the browser window to make everything
        visible or we have to be scrolling to each element when that happens.
        """
        self.selenium.get(self.live_server_url)
        logging.info(f"Opened: {self.live_server_url}")
        logging.info(f"Title: {self.selenium.title}")
        self.selenium.set_window_size(500, 2000)

    def _login(self, user, password):
        self.selenium.get(self.live_server_url)
        # The home page will probably be the login page, but to make sure that
        # we reach the login page, we open de burger menu and navigate to
        # sign-in.
        self.burger_menu_action()
        login_menu_option = self.selenium.find_element(By.ID, "menu_login")
        login_menu_option.click()
        logging.info(f"Opened: {self.selenium.current_url}")
        logging.info(f"Title: {self.selenium.title}")

        login_user = self.selenium.find_element(By.ID, "id_username")
        login_password = self.selenium.find_element(By.ID, "id_password")

        login_user.send_keys(user)
        login_password.send_keys(password)
        login_password.send_keys(Keys.RETURN)

    def _admin_login(self):
        self._login(
            settings.DJANGO_SUPERUSER_EMAIL,
            settings.DJANGO_SUPERUSER_PASSWORD,
        )
        self.burger_menu_action()
        admin_menu = self.selenium.find_element(By.ID, "menu_admin")
        admin_menu.click()

        self.logging_url_title_and_assert_title(Strings.ADMIN_TITLE.value)
        logging.info("Logged in to admin with initial superuser.")

    def _signup(self):
        # Log out to return to the home page
        admin_menu = self.select_element_by_text(Strings.LOGOUT.value)
        admin_menu.click()

        # Open the main menu to select the Sign Up option.
        self.burger_menu_action()

        signup_menu_option = self.selenium.find_element(By.ID, "menu_signup")
        signup_menu_option.click()

        self.logging_url_title_and_assert_title(Strings.SIGNUP_TITLE.value)

        signup_name = self.selenium.find_element(By.ID, "id_name")
        signup_surnames = self.selenium.find_element(By.ID, "id_surnames")
        signup_password1 = self.selenium.find_element(By.ID, "id_password1")
        signup_password2 = self.selenium.find_element(By.ID, "id_password2")
        signup_email = self.selenium.find_element(By.ID, "id_email")
        signup_accept_conditions = self.selenium.find_element(
            By.ID, "id_accept_conditions"
        )

        signup_name.send_keys(self.sample_data["first_user"].name)
        signup_surnames.send_keys(self.sample_data["first_user"].surnames)
        signup_password1.send_keys(self.sample_data["first_user"].password)
        signup_password2.send_keys(self.sample_data["first_user"].password)
        signup_email.send_keys(self.sample_data["first_user"].email)
        signup_accept_conditions.click()
        signup_password2.send_keys(Keys.RETURN)

        self.logging_url_title_and_assert_title(Strings.PROFILE_TITLE.value)

    def _verify_email(self):
        # Verify email
        button_alert = self.selenium.find_element(By.ID, "id_verify_email")
        button_alert.click()

        self.logging_url_title_and_assert_title(Strings.EMAIL_VALIDATION_TITLE.value)

        # Click on the button to send the verification email.
        send_button = self.selenium.find_element(By.ID, "id_submit")
        send_button.click()

        # Wait for the verification email to be sent.
        self._check_mail_sent(
            self.sample_data["first_user"].email,
            self.sample_data["first_user"].name,
        )
        verification_code = self.selenium.find_element(
            By.ID, "id_email_verification_code"
        )
        self.user = User.objects.filter(
            email=self.sample_data["first_user"].email
        ).first()
        verification_code.send_keys(self.user.email_verification_code)
        verification_code.send_keys(Keys.RETURN)

        # Template confirm account has been successfully verified.
        # Click on the button Go Back.
        logging.info("Verified email.")

        go_back = self.select_element_by_text("Go back")
        go_back.click()

    def _update_profile(self):
        # Back to profile page.
        self.logging_url_title_and_assert_title(Strings.PROFILE_TITLE.value)

        update_name = self.selenium.find_element(By.ID, "id_name")
        update_surnames = self.selenium.find_element(By.ID, "id_surnames")

        # Update the profile | Name & Surnames.
        update_name.clear()
        update_surnames.clear()
        update_name.send_keys("Andrews")
        update_surnames.send_keys("McDolls")

        update_surnames.send_keys(Keys.RETURN)

        self.logging_url_title_and_assert_title(Strings.REGISTRY_UPDATE_TITLE.value)

        button_back = self.selenium.find_element(By.ID, "id_back")
        button_back.click()

        self.logging_url_title_and_assert_title(Strings.PROFILE_TITLE.value)

        # Update the profile | Email.
        update_email = self.selenium.find_element(By.ID, "id_email")
        update_email.clear()
        update_email.send_keys("andrews.mcdolls@gmail.com")
        self.user.email = "andrews.mcdolls@gmail.com"
        self.user.save()
        update_email.send_keys(Keys.RETURN)

        self.logging_url_title_and_assert_title(Strings.REGISTRY_UPDATE_TITLE.value)

        button_back = self.selenium.find_element(By.ID, "id_back")
        button_back.click()

        # Verify again the e-mail again after changing it
        button_alert = self.selenium.find_element(By.ID, "id_verify_email")
        button_alert.click()

        self.logging_url_title_and_assert_title(Strings.EMAIL_VALIDATION_TITLE.value)

        # Click on the button to send the verification email.
        send_button = self.selenium.find_element(By.ID, "id_submit")
        send_button.click()

        verification_code = self.selenium.find_element(
            By.ID, "id_email_verification_code"
        )
        code = (
            User.objects.filter(email=self.user.email).first().email_verification_code
        )
        verification_code.send_keys(code)
        verification_code.send_keys(Keys.RETURN)

        # Template confirm account has been successfully verified.
        # Click on the button Go Back.
        logging.info("Verified email.")

        go_back = self.selenium.find_element(By.ID, "id_back")
        go_back.click()

    def _password_change(self):
        self.logging_url_title_and_assert_title(Strings.PROFILE_TITLE.value)

        # Change password.
        button_password_change = self.selenium.find_element(By.ID, "id_password_change")
        button_password_change.click()

        self.logging_url_title_and_assert_title(Strings.PASSWORD_CHANGE_TITLE.value)

        old_password = self.selenium.find_element(By.ID, "id_old_password")
        old_password.send_keys(self.sample_data["first_user"].password)
        new_password = self.selenium.find_element(By.ID, "id_new_password1")
        new_password.send_keys("0pl#4jT7m8ijn")
        password_confirmation = self.selenium.find_element(By.ID, "id_new_password2")
        password_confirmation.send_keys("0pl#4jT7m8ijn")
        password_confirmation.send_keys(Keys.RETURN)

        self.logging_url_title_and_assert_title(Strings.PASSWORD_CHANGE_TITLE.value)

        # Click on the button Go Back.
        go_back = self.selenium.find_element(By.ID, "id_back")
        go_back.click()

        self.logging_url_title_and_assert_title(Strings.PROFILE_TITLE.value)

    def _home(self):
        # Open the main menu to select the Home option.
        self.burger_menu_action()
        home_menu_option = self.selenium.find_element(By.ID, "menu_home")
        home_menu_option.click()

        self.logging_url_title_and_assert_title(Strings.DEMO_TITLE.value)

    def _demo_list(self):
        # Open the main menu to select the Home option.
        self.burger_menu_action()
        home_menu_option = self.selenium.find_element(By.ID, "menu_demo")
        home_menu_option.click()

        self.logging_url_title_and_assert_title(Strings.DEMO_TITLE.value)

    def _demo_create(self):
        # Click on Create New Data to create a new record.
        create_data = self.selenium.find_element(By.ID, "id_create_data")
        create_data.click()
        self.logging_url_title_and_assert_title(Strings.DEMO_CREATE.value)

        # All the fields are filled in
        demo_field_text_1 = self.selenium.find_element(By.NAME, "field_text_1")
        demo_field_text_2 = self.selenium.find_element(By.NAME, "field_text_2")
        demo_field_email = self.selenium.find_element(By.NAME, "field_email")
        demo_field_radio = self.selenium.find_element(By.ID, "id_field_radio_1")
        demo_field_boolean_checkbox = self.selenium.find_element(
            By.NAME, "field_boolean_checkbox"
        )
        demo_field_select_dropdown = self.selenium.find_element(
            By.NAME, "field_select_dropdown"
        )
        demo_field_password = self.selenium.find_element(By.NAME, "field_password")
        demo_field_password_confirm = self.selenium.find_element(
            By.NAME, "field_password_confirm"
        )
        demo_field_number = self.selenium.find_element(By.NAME, "field_number")

        demo_field_text_1.send_keys("text_1")
        demo_field_text_2.send_keys("text_2")
        demo_field_email.send_keys("email@test.com")
        demo_field_radio.click()
        demo_field_boolean_checkbox.click()
        demo_field_select_dropdown.send_keys("OP2")
        demo_field_password.send_keys("password")
        demo_field_password_confirm.send_keys("password")
        demo_field_number.send_keys("1234")
        demo_field_password.send_keys(Keys.RETURN)

        self.logging_url_title_and_assert_title(Strings.DEMO_TITLE.value)

    def _demo_details(self):
        # Click on data entry
        data_id = Data.objects.values_list("id", flat=True).first()
        data_button = self.selenium.find_element(By.ID, f"id_details_{data_id}")
        data_button.click()

        self.logging_url_title_and_assert_title(Strings.DEMO_DETAILS.value)

    def _demo_update(self):
        # Click on Edit Data to update record.
        update_data = self.selenium.find_element(By.ID, "id_edit")
        update_data.click()
        self.logging_url_title_and_assert_title(Strings.DEMO_UPDATE.value)

        # Data Updated
        update_field_text_1 = self.selenium.find_element(By.ID, "id_field_text_1")
        update_field_text_2 = self.selenium.find_element(By.ID, "id_field_text_2")
        update_field_email = self.selenium.find_element(By.ID, "id_field_email")
        update_field_radio = self.selenium.find_element(By.ID, "id_field_radio_1")
        update_field_select_dropdown = self.selenium.find_element(
            By.NAME, "field_select_dropdown"
        )
        update_field_password = self.selenium.find_element(By.NAME, "field_password")
        update_field_password_confirm = self.selenium.find_element(
            By.NAME, "field_password_confirm"
        )
        update_field_number = self.selenium.find_element(By.NAME, "field_number")

        update_field_text_1.clear()
        update_field_text_2.clear()
        update_field_email.clear()
        update_field_password.clear()
        update_field_password_confirm.clear()
        update_field_number.clear()
        update_field_text_1.send_keys("update_text_1")
        update_field_text_2.send_keys("update_text_2")
        update_field_email.send_keys("update_email@test.com")
        update_field_radio.click()
        update_field_select_dropdown.send_keys("OP3")
        update_field_password.send_keys("update_password")
        update_field_password_confirm.send_keys("update_password")
        update_field_number.send_keys("5678")
        update_submit = self.selenium.find_element(By.ID, "id_submit")
        update_submit.click()

        self.logging_url_title_and_assert_title(Strings.DEMO_DETAILS.value)
