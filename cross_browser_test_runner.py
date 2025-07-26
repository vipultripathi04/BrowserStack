import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import WebDriverException, TimeoutException

from elpais_scraper import scrape_and_analyze_articles

BROWSERSTACK_USERNAME = "Your BROWSERSTACK_USERNAME"
BROWSERSTACK_ACCESS_KEY = "Your BROWSERSTACK_ACCESS_KEY"
URL = "https://hub-cloud.browserstack.com/wd/hub"

capabilities = [
    {
        'browserName': 'Chrome',
        'browserVersion': 'latest',
        'platformName': 'WINDOWS',
        'name': 'Chrome Test',
        'build': 'Selenium-BS'
    },
    {
        'browserName': 'Firefox',
        'browserVersion': 'latest', 
        'platformName': 'MAC',
        'name': 'Firefox Test',
        'build': 'Selenium-BS'
    },

    {
        'browserName': 'Edge',
        'browserVersion': 'latest',
        'platformName': 'WINDOWS',
        'name': 'Edge Test', 
        'build': 'Selenium-BS'
    }
]

def create_driver_with_capabilities(caps):
    """Create WebDriver with proper options for Selenium 4.x"""
    
    # Create options based on browser type
    browser = caps.get('browser', caps.get('browserName', '')).lower()
    
    if 'chrome' in browser or caps.get('browserName') == 'chrome':
        options = ChromeOptions()
    elif 'firefox' in browser:
        options = FirefoxOptions()
    elif 'edge' in browser:
        options = EdgeOptions()
    else:
        # For mobile devices or other browsers, use ChromeOptions as fallback
        options = ChromeOptions()
    
    # Set BrowserStack capabilities using the secure method
    options.set_capability('bstack:options', {
        'userName': BROWSERSTACK_USERNAME,
        'accessKey': BROWSERSTACK_ACCESS_KEY,
        'buildName': caps.get('build', 'Selenium-Test'),
        'sessionName': caps.get('name', 'Test Session'),
        'local': False,
        'debug': True,
        'networkLogs': True
    })
    
    # Set browser-specific capabilities
    for key, value in caps.items():
        if key not in ['build', 'name']:  # Skip already handled keys
            options.set_capability(key, value)
    
    # Create driver with secure connection
    return webdriver.Remote(
        command_executor=URL,
        options=options,
        keep_alive=True
    )

def run_test(caps):
    driver = None
    test_name = caps.get('name', caps.get('device', 'Unknown Test'))
    
    try:
        driver = create_driver_with_capabilities(caps)
        result = scrape_and_analyze_articles(driver)
        
        # Set BrowserStack test status based on result
        if result.get('status') == 'success':
            driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Test completed successfully"}}')
        else:
            driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "' + str(result.get('reason', 'Unknown error')) + '"}}')
        
        return result
        
    except Exception as e:
        # Set failed status in BrowserStack
        if driver:
            try:
                driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "' + str(e)[:100] + '"}}')
            except:
                pass
        raise Exception(f"Test {test_name} failed: {str(e)}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass 

def execute_cross_browser_tests():
    print(f"Running {len(capabilities)} cross-browser tests...")
    
    results = []
    failed_tests = []
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit all tasks
            future_to_caps = {executor.submit(run_test, caps): caps for caps in capabilities}
            
            # Process completed tasks
            for future in concurrent.futures.as_completed(future_to_caps):
                caps = future_to_caps[future]
                test_name = caps.get('name', caps.get('device', 'Unknown Test'))
                
                try:
                    result = future.result(timeout=300)  # 5 minute timeout per test
                    results.append((test_name, "SUCCESS", result))
                    print(f"{test_name}")
                except Exception as e:
                    failed_tests.append((test_name, str(e)))
                    results.append((test_name, "FAILED", str(e)))
                    print(f"{test_name}: {str(e)[:50]}...")
    
    except Exception as e:
        print(f"Critical error: {str(e)}")
    
    finally:
        successful = len([r for r in results if r[1] == 'SUCCESS'])
        print(f"\nResults: {successful}/{len(capabilities)} successful")
        
        if failed_tests:
            print("Failed tests:")
            for test_name, error in failed_tests:
                print(f"  {test_name}: {error[:50]}...")

if __name__ == "__main__":
    execute_cross_browser_tests()