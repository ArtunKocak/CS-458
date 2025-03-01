from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import time, re
import unittest
    #test case 1 --> valid/invalid login
    #test case 2 --> valid/invalid google login
    #test case 3 --> check multiple user log in behavior on different browsers or incognito mode
    #test case 4 --> multiple failed login attempts session lockout 30 seconds
    #test case 5 --> incorrect form inputs (blank, invalid email/phone formats, leading/trailing spaces)
class LoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        #cls.driver = webdriver.Chrome()
        cls.driver = uc.Chrome()        #normal google chrome blocks selenium logins
        cls.driver.get("http://127.0.0.1:5000/login")
        cls.driver.maximize_window()
        
    def setUp(self):
        """Ensure a fresh session before each test"""
        self.driver.get("http://127.0.0.1:5000/login")
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")
        try:
            logout_button = self.driver.find_element(By.ID, "logoutButton")  
            logout_button.click()
            time.sleep(1)
        except:
            pass

    #---------------##########      TEST CASE 1         #########--------------------
    def test_valid_email_login(self):
        """TC001 - Login with a valid email and password"""
        driver = self.driver
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("admin@gmail.com")
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        WebDriverWait(driver, 10).until(EC.url_contains("http://127.0.0.1:5000/"))
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/")      #should be redirected to home
        cookies = driver.get_cookies()
        session_cookie = next((cookie for cookie in cookies if cookie['name'] == 'session'), None)
        self.assertIsNotNone(session_cookie, "Session cookie should exist after login.")

    def test_valid_phone_login(self):
        """TC002 - Login with a valid phone number and password"""
        driver = self.driver
        phone_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        phone_input.clear()
        phone_input.send_keys("+1234567890")
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        WebDriverWait(driver, 10).until(EC.url_contains("http://127.0.0.1:5000/"))
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/")      #should be redirected to home
        cookies = driver.get_cookies()
        session_cookie = next((cookie for cookie in cookies if cookie['name'] == 'session'), None)
        self.assertIsNotNone(session_cookie, "Session cookie should exist after login.")

    def test_invalid_login(self):
        """TC003 - Login with invalid credentials (Should not redirect)"""
        driver = self.driver
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("wronguser@gmail.com")
        password_input.clear()
        password_input.send_keys("wrongpassword")
        login_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login") #should be redirected to login again
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Invalid credentials.")
        cookies = driver.get_cookies()
        session_cookie = next((cookie for cookie in cookies if cookie['name'] == 'session'), None)
        self.assertIsNotNone(session_cookie, "Session cookie should exist even after invalid login.")   #session must exist to track # invalid attempts

    #---------------##########      TEST CASE 2         #########--------------------
    def test_valid_google_login(self):
        """TC004 - Test Google Login"""
        driver = self.driver
        google_login_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "googleLoginButton")))
        google_login_button.click()
        WebDriverWait(driver, 20).until(EC.url_contains("accounts.google.com"))
        email_input = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.NAME, "identifier")))
        email_input.send_keys("interalyze@gmail.com")
        email_input.send_keys(Keys.RETURN)
        next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "identifierNext")))
        driver.execute_script("arguments[0].click();", next_button)
        password_input = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
        password_input.send_keys("Interalyze_24Proje")
        password_input.send_keys(Keys.RETURN)
        continue_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button/span[contains(text(), 'Continue')]")))
        driver.execute_script("arguments[0].click();", continue_button)
        WebDriverWait(driver, 30).until(EC.url_to_be("http://127.0.0.1:5000/"))
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/")
        cookies = driver.get_cookies()
        session_cookie = next((cookie for cookie in cookies if cookie['name'] == 'session'), None)
        self.assertIsNotNone(session_cookie, "Session cookie should exist after login.")

    def test_invalid_google_login(self):
        """TC005 - Test Google Login with Invalid Credentials"""
        driver = self.driver
        google_login_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "googleLoginButton")))
        google_login_button.click()
        WebDriverWait(driver, 20).until(EC.url_contains("accounts.google.com"))
        email_input = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.NAME, "identifier")))
        email_input.send_keys("invalidemail333@gmail.com")
        email_input.send_keys(Keys.RETURN)
        error_message = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Couldn’t find your Google Account')]")))
        self.assertIsNotNone(error_message, "Error message should be displayed for invalid email")
        driver.get("http://127.0.0.1:5000/login")
        google_login_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "googleLoginButton")))
        google_login_button.click()
        WebDriverWait(driver, 20).until(EC.url_contains("accounts.google.com"))
        email_input = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.NAME, "identifier")))
        email_input.clear()
        email_input.send_keys("interalyze@gmail.com")
        email_input.send_keys(Keys.RETURN)
        next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "identifierNext")))
        driver.execute_script("arguments[0].click();", next_button)
        password_input = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
        password_input.send_keys("WrongPassword123")
        password_input.send_keys(Keys.RETURN)
        WebDriverWait(driver, 20).until(EC.url_contains("accounts.google.com"))
        self.assertTrue("accounts.google.com" in driver.current_url, "Should remain on Google login page after failed attempt")
        cookies = driver.get_cookies()
        session_cookie = next((cookie for cookie in cookies if cookie['name'] == 'session'), None)
        self.assertIsNone(session_cookie, "Session cookie should NOT exist after failed login")

    #---------------##########      TEST CASE 3         #########--------------------
    def test_two_parallel_logins(self):
        """Test logging in with two different accounts in the same test""" #one chrome + one incognito
        driver1 = webdriver.Chrome()
        driver1.get("http://127.0.0.1:5000/login")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")
        driver2 = webdriver.Chrome(options=chrome_options)
        driver2.get("http://127.0.0.1:5000/login")
        email1 = driver1.find_element(By.ID, "user_input")
        password1 = driver1.find_element(By.ID, "password")
        login_button1 = driver1.find_element(By.ID, "loginButton")
        email1.send_keys("admin@gmail.com")
        password1.send_keys("password123")
        login_button1.click()
        WebDriverWait(driver1, 10).until(EC.url_contains("http://127.0.0.1:5000/"))
        print("First user logged in:", driver1.current_url)
        email2 = driver2.find_element(By.ID, "user_input")
        password2 = driver2.find_element(By.ID, "password")
        login_button2 = driver2.find_element(By.ID, "loginButton")
        email2.send_keys("admin2@gmail.com")
        password2.send_keys("password123")
        login_button2.click()
        WebDriverWait(driver2, 10).until(EC.url_contains("http://127.0.0.1:5000/"))
        print("Second user logged in:", driver2.current_url)
        cookies1 = driver1.get_cookies()
        cookies2 = driver2.get_cookies()
        session_cookie1 = next((cookie for cookie in cookies1 if cookie['name'] == 'session'), None)
        session_cookie2 = next((cookie for cookie in cookies2 if cookie['name'] == 'session'), None)
        assert session_cookie1 is not None, "Session cookie should exist for first user."
        assert session_cookie2 is not None, "Session cookie should exist for second user."
        assert session_cookie1 != session_cookie2, "Sessions should be different for each user."
        driver1.quit()
        driver2.quit()
    #---------------##########      TEST CASE 4         #########--------------------
    def test_multiple_failed_logins(self):
        """TC006 - Multiple failed login attempts should lock the session temporarily (30 seconds)"""
        driver = self.driver
        for i in range(3):
            email_input = driver.find_element(By.ID, "user_input")
            password_input = driver.find_element(By.ID, "password")
            login_button = driver.find_element(By.ID, "loginButton")
            email_input.clear()
            email_input.send_keys("admin@gmail.com")
            password_input.clear()
            password_input.send_keys("wrongpassword")
            login_button.click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "errorMessage")))
            error_message = driver.find_element(By.ID, "errorMessage").text
            self.assertEqual(error_message, "Invalid credentials.")
        # After 3 failed attempts, the system should not lock the session yet
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertNotRegex(error_message, r"Too many failed attempts. Please try again in (\d+) seconds.", 
                            "System should not show lock message after 3 failed attempts.")
        # After 4 failed attempts, the system should lock the session for 30 seconds
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("admin@gmail.com")
        password_input.clear()
        password_input.send_keys("wrongpassword")
        login_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        match = re.search(r"Too many failed attempts. Please try again in (\d+) seconds.", error_message)
        self.assertIsNotNone(match, "System should display a lock message with countdown after 4th failed attempt.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login")     #should still be in the login page
        cookies = driver.get_cookies()
        session_cookie = next((cookie for cookie in cookies if cookie['name'] == 'session'), None)
        self.assertIsNotNone(session_cookie, "Session cookie should exist after failed login attempts.")
        time.sleep(30)
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("admin@gmail.com")
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/")

    #---------------##########      TEST CASE 5         #########--------------------
    def test_blank_fields(self):
        driver = self.driver
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        #Blank email/phone with valid password
        email_input.clear()
        email_input.send_keys("")
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Email/Phone field is required.", "Error message for blank email/phone is incorrect.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login")     #should still be in login
        #Valid email/phone and blank password
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("admin@gmail.com")
        password_input.clear()
        password_input.send_keys("")
        login_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Password field is required.", "Error message for blank password is incorrect.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login")     #should still be in login
        #Both fields blank
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("")
        password_input.clear()
        password_input.send_keys("")
        login_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Email/Phone and Password are required.", "Error message for both blank fields is incorrect.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login")     #should still be in login

    def test_leading_and_trailing_spaces(self):
        driver = self.driver
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("   admin@gmail.com   ")
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/")      #should redirect to home

    def test_invalid_email_and_phone_format(self):
        driver = self.driver
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("admin.gmail.com")  #missing '@'
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Invalid email or phone number format.", "Error message for invalid email format is incorrect.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login")     #should still be in login
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("1234")     #invalid phone number
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Invalid email or phone number format.", "Error message for invalid phone number format is incorrect.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login")     #should still be in login
        email_input = driver.find_element(By.ID, "user_input")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        email_input.clear()
        email_input.send_keys("admin@@gmail.com")  #extra '@'
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "errorMessage")))
        error_message = driver.find_element(By.ID, "errorMessage").text
        self.assertEqual(error_message, "Invalid email or phone number format.", "Error message for invalid email format is incorrect.")
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login")     #should still be in login


    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
