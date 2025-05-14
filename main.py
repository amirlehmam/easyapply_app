import yaml, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from validate_email import validate_email
from linkedineasyapply import LinkedinEasyApply
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("easyapply-bot")

def init_browser():
    browser_options = Options()
    # Recommended options for headless/cloud environments
    options = [
        '--disable-blink-features',
        '--no-sandbox',
        '--disable-extensions',
        '--ignore-certificate-errors',
        '--disable-blink-features=AutomationControlled',
        '--disable-gpu',
        '--disable-software-rasterizer',
        '--disable-dev-shm-usage',
        '--headless=new',  # Use new headless mode for Chrome 112+
        '--window-size=1920,1080',
        '--remote-debugging-port=9222',
    ]
    for opt in options:
        browser_options.add_argument(opt)

    # Set Chrome binary location from environment variable if provided
    chrome_binary = os.environ.get('CHROME_BINARY')
    if chrome_binary:
        browser_options.binary_location = chrome_binary
        logger.info(f"Using Chrome binary at: {chrome_binary}")
    else:
        logger.warning("CHROME_BINARY environment variable not set. Using default Chrome location.")

    try:
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=browser_options)
        driver.implicitly_wait(1)  # Wait time in seconds to allow loading of elements
        # driver.set_window_position(0, 0)
        # driver.maximize_window()
        return driver
    except Exception as e:
        logger.error(f"Error initializing Chrome WebDriver: {e}")
        logger.error("Make sure Google Chrome is installed and CHROME_BINARY is set if Chrome is not in the default location.")
        raise

def validate_yaml(config_path="config.yaml"):
    with open(config_path, 'r', encoding='utf-8') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(f"YAML validation error: {exc}")
            raise exc

    mandatory_params = ['email',
                        'password',
                        'disableAntiLock',
                        'remote',
                        'lessthanTenApplicants',
                        'newestPostingsFirst',
                        'experienceLevel',
                        'jobTypes',
                        'date',
                        'positions',
                        'locations',
                        'residentStatus',
                        'distance',
                        'outputFileDirectory',
                        'checkboxes',
                        'universityGpa',
                        'languages',
                        'experience',
                        'personalInfo',
                        'eeo',
                        'uploads']

    for mandatory_param in mandatory_params:
        if mandatory_param not in parameters:
            error_msg = f"{mandatory_param} is not defined in the config.yaml file!"
            logger.error(error_msg)
            raise Exception(error_msg)

    assert validate_email(parameters['email'])
    assert len(str(parameters['password'])) > 0
    assert isinstance(parameters['disableAntiLock'], bool)
    assert isinstance(parameters['remote'], bool)
    assert isinstance(parameters['lessthanTenApplicants'], bool)
    assert isinstance(parameters['newestPostingsFirst'], bool)
    assert isinstance(parameters['residentStatus'], bool)
    assert len(parameters['experienceLevel']) > 0
    experience_level = parameters.get('experienceLevel', [])
    at_least_one_experience = False

    for key in experience_level.keys():
        if experience_level[key]:
            at_least_one_experience = True
    assert at_least_one_experience

    assert len(parameters['jobTypes']) > 0
    job_types = parameters.get('jobTypes', [])
    at_least_one_job_type = False
    for key in job_types.keys():
        if job_types[key]:
            at_least_one_job_type = True

    assert at_least_one_job_type
    assert len(parameters['date']) > 0
    date = parameters.get('date', [])
    at_least_one_date = False

    for key in date.keys():
        if date[key]:
            at_least_one_date = True
    assert at_least_one_date

    approved_distances = {0, 5, 10, 25, 50, 100}
    assert parameters['distance'] in approved_distances
    assert len(parameters['positions']) > 0
    assert len(parameters['locations']) > 0
    assert len(parameters['uploads']) >= 1 and 'resume' in parameters['uploads']
    assert len(parameters['checkboxes']) > 0

    checkboxes = parameters.get('checkboxes', [])
    assert isinstance(checkboxes['driversLicence'], bool)
    assert isinstance(checkboxes['requireVisa'], bool)
    assert isinstance(checkboxes['legallyAuthorized'], bool)
    assert isinstance(checkboxes['certifiedProfessional'], bool)
    assert isinstance(checkboxes['urgentFill'], bool)
    assert isinstance(checkboxes['commute'], bool)
    assert isinstance(checkboxes['backgroundCheck'], bool)
    assert isinstance(checkboxes['securityClearance'], bool)
    assert 'degreeCompleted' in checkboxes
    assert isinstance(parameters['universityGpa'], (int, float))

    languages = parameters.get('languages', [])
    language_types = {'none', 'conversationnel', 'professionnel', 'natif ou bilingue'}
    for language in languages:
        assert languages[language].lower() in language_types

    experience = parameters.get('experience', [])
    for tech in experience:
        assert isinstance(experience[tech], int)
    assert 'default' in experience

    assert len(parameters['personalInfo'])
    personal_info = parameters.get('personalInfo', [])
    for info in personal_info:
        assert personal_info[info] != ''

    assert len(parameters['eeo'])
    eeo = parameters.get('eeo', [])
    for survey_question in eeo:
        assert eeo[survey_question] != ''

    if parameters.get('openaiApiKey') == 'sk-proj-your-openai-api-key':
        # Overwrite the default value with None to indicate internally that the OpenAI API key is not configured
        logger.info("OpenAI API key not configured. Defaulting to empty responses for text fields.")
        parameters['openaiApiKey'] = None

    return parameters

def run_bot(config_path="config.yaml"):
    """
    Run the bot with the specified configuration
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        The bot instance
    """
    logger.info("Starting LinkedIn EasyApply Bot")
    parameters = validate_yaml(config_path)
    browser = init_browser()

    bot = LinkedinEasyApply(parameters, browser)
    bot.login()
    bot.security_check()
    bot.start_applying()
    
    return bot

if __name__ == '__main__':
    try:
        run_bot()
    except Exception as e:
        logger.error(f"Error running bot: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())