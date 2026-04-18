import csv
import json
import logging
from functools import wraps
from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from requests.exceptions import HTTPError

from deps_iam.constants import API_KEY, API_PREFIX

INNER_IAM_URL = f"http://localhost:8000{API_PREFIX}"
DEPS_TOKEN_HEADER = "deps-token"


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S",
)
logging.addLevelName(logging.CRITICAL, "\033[5;31m%s\033[1;0m" % logging.getLevelName(logging.CRITICAL))
logger = logging.getLogger(__name__)


def request_error_handler(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except HTTPError as err:
            logger.error(f"HTTP error occurs in {func.__name__} step. {err}.")
            raise SystemExit
        except Exception as err:
            logger.error(f"Unexpected error occurs in {func.__name__} step. {err}.")
            raise SystemExit
        return result

    return inner


def create_api_key_header(api_key: str) -> Dict[str, Any]:
    return {API_KEY: api_key}


def create_deps_token_header(deps_token: Dict[str, Any]) -> Dict[str, Any]:
    return {DEPS_TOKEN_HEADER: json.dumps(deps_token)}


@request_error_handler
def create_service_account(account_name: str, organisation_pk: Optional[str] = None) -> str:
    url = f"{INNER_IAM_URL}/users"

    body: dict = {
        "user": {
            "email": account_name,
        },
        "createAPIKey": True,
    }

    if organisation_pk:
        body["user"]["organisation"] = organisation_pk

    response = requests.post(url=url, json=body)

    if response.status_code == HTTPStatus.CONFLICT:
        logger.error(f"Service account {account_name} already exists.")
        raise SystemExit

    response.raise_for_status()

    api_key = response.headers[API_KEY]

    logger.info(f"Service account {account_name} successfully created. API Key - {api_key}")

    return api_key


@request_error_handler
def get_deps_token(api_key: str) -> Dict[str, Any]:
    url = f"{INNER_IAM_URL}/authorize"

    response = requests.get(url=url, headers=create_api_key_header(api_key))

    response.raise_for_status()

    return json.loads(response.headers[DEPS_TOKEN_HEADER])


@request_error_handler
def create_organisation(
    deps_token: Dict[str, Any], organisation_name: str, customization_url: Optional[str] = None
) -> str:
    url = f"{INNER_IAM_URL}/organisations"

    body = {
        "name": organisation_name,
    }
    if customization_url:
        body["customizationUrl"] = customization_url

    response = requests.post(url=url, json=body, headers=create_deps_token_header(deps_token))
    response.raise_for_status()

    logger.info(f"Organisation {organisation_name} account successfully created.")

    return response.json()["pk"]


@request_error_handler
def activate_user_organisation(deps_token: Dict[str, Any], organisation_pk: str) -> str:
    url = f"{INNER_IAM_URL}/organisations/{organisation_pk}/activate"

    response = requests.post(url=url, headers=create_deps_token_header(deps_token))
    response.raise_for_status()

    return response.json()["name"]


@request_error_handler
def get_user_organisations(deps_token: Dict[str, Any]) -> list[dict[str, str]]:
    url = f"{INNER_IAM_URL}/organisations"

    response = requests.get(url=url, headers=create_deps_token_header(deps_token))
    response.raise_for_status()

    return response.json()


@request_error_handler
def invite_users(
    deps_token: Dict[str, Any], organisation_pk: str, email_list: list[dict[str, str]]
) -> list[dict[str, str]]:
    url = f"{INNER_IAM_URL}/organisations/{organisation_pk}/invite"

    response = requests.post(url=url, headers=create_deps_token_header(deps_token), json=email_list)
    response.raise_for_status()

    return response.json()


def iam_init_script(
    organisation_name: Optional[str],
    organisation_pk: Optional[str],
    service_account: Optional[str],
    api_key: Optional[str],
    invite_list: Optional[Path],
    customization_url: Optional[str],
) -> None:
    # If no api key then create service account
    if api_key is None:
        api_key = create_service_account(account_name=service_account, organisation_pk=organisation_pk)

    deps_token = get_deps_token(api_key)
    logger.info(f"DEPS Token - {json.dumps(deps_token)}")

    if service_account is None:
        service_account = deps_token["email"]
        logger.info(f"Using existing service account {service_account}")

    # If no existing organisation create new one with name `organisation_name`
    if organisation_pk is None:
        organisation_pk = create_organisation(
            deps_token, organisation_name=organisation_name, customization_url=customization_url
        )
        organisation_name = activate_user_organisation(deps_token, organisation_pk)
        deps_token["organisation"] = organisation_pk

        logger.info(f"Account `{service_account}` was successfully added to organisation `{organisation_name}`.")
    else:
        # Check if user is a member of given organisation
        user_organisations = get_user_organisations(deps_token)
        if not [organisation for organisation in user_organisations if organisation["pk"] == organisation_pk]:
            raise SystemExit(f"User {service_account} is not a member of organisation `{organisation_pk}`")
        organisation_name = activate_user_organisation(deps_token=deps_token, organisation_pk=organisation_pk)

        if customization_url is not None:
            logging.warning("No new organisation created, `--customization_url` ignored")

    if invite_list is not None:
        with open(invite_list, newline="") as csvfile:
            invite_list_reader = csv.DictReader(csvfile)
            if invite_list_reader.fieldnames != ["email"]:
                raise SystemExit("Wrong csv file format. Must contain only one column `email`")

            invited_users = invite_users(
                deps_token=deps_token, organisation_pk=organisation_pk, email_list=list(invite_list_reader)
            )
            logger.info(
                f"Invited users to organisation `{organisation_name}`:\n"
                f"{', '.join(user['email'] for user in invited_users)}"
            )
