import os
from selenium import webdriver

BROWSERSTACK_USERNAME = os.getenv("BROWSERSTACK_USERNAME")
BROWSERSTACK_ACCESS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY")

HUB_URL = f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"


def get_remote_driver(bstack_options: dict, browser_name: str = "Chrome", browser_version: str = "latest"):
    """
    bstack_options: dictionary with keys like os, osVersion, deviceName, realMobile, sessionName, local, etc.
    Example usage: get_remote_driver(EXAMPLE_CAPS[0])
    """
    caps = {
        "browserName": browser_name,
        "browserVersion": browser_version,
        "bstack:options": bstack_options,
    }
    driver = webdriver.Remote(command_executor=HUB_URL, desired_capabilities=caps)
    return driver


# Example capability matrix you can parametrize in pytest
EXAMPLE_CAPS = [
    {
        "os": "Windows",
        "osVersion": "11",
        "sessionName": "ElPais - Chrome Desktop",
        "local": "false",
    },
    {
        "os": "OS X",
        "osVersion": "Ventura",
        "sessionName": "ElPais - Safari Desktop",
        "local": "false",
    },
    {
        "deviceName": "iPhone 14",
        "osVersion": "16.0",
        "realMobile": "true",
        "sessionName": "ElPais - iPhone 14",
    },
    {
        "deviceName": "Google Pixel 7",
        "osVersion": "13.0",
        "realMobile": "true",
        "sessionName": "ElPais - Pixel 7",
    },
    {
        "os": "Windows",
        "osVersion": "10",
        "browserName": "Edge",
        "browserVersion": "latest",
        "sessionName": "ElPais - Edge",
        "local": "false",
    },
]
