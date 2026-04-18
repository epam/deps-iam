from pathlib import Path
from typing import Optional

import click

from deps_iam.app import (
    run_api,
    run_consumer,
    run_initialization,
    run_polling_publisher,
)
from deps_iam.scripts.iam_init import iam_init_script


@click.group()
def cli() -> None:
    pass


@cli.command()
def serve() -> None:
    run_api()


@cli.command()
def consume() -> None:
    run_consumer()


@cli.command(name="run_message_polling")
def run_message_polling() -> None:
    run_polling_publisher()


@cli.command(name="iam_init")
@click.option("--organisation_name", type=str, help="New organisation name")
@click.option("--organisation_pk", type=str, help="Existing organisation pk")
@click.option("--service_account", type=str, help="Service account name (email)")
@click.option("--api_key", type=str, help="Service account API key")
@click.option(
    "--invite_list",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    help="`.csv` file with a list of emails to be invited",
)
@click.option("--customization_url", type=str, help="Organisation customization url")
def iam_init(
    organisation_name: Optional[str],
    organisation_pk: Optional[str],
    service_account: Optional[str],
    api_key: Optional[str],
    invite_list: Optional[Path],
    customization_url: Optional[str],
) -> None:
    """Initialize the service.

    Note: --organisation_name and --organisation_pk are mutually exclusive.
    Note: --service_account and --api_key are mutually exclusive.
    Note: --organisation_pk and --service_account are mutually exclusive.
    Note: If `--organisation_name` is not provided `--customization_url` will be ignored.
    """
    if (organisation_name is None) == (organisation_pk is None):
        raise SystemExit("Must provide either `organisation_name` or `organisation_pk`, but not both")
    if (service_account is None) == (api_key is None):
        raise SystemExit("Must provide either `service_account` or `api_key`, but not both")
    if organisation_pk is not None and service_account is not None:
        raise SystemExit(
            "Must not provide both `organisation_pk` and `service_account`, "
            "can not create a service account in existing organisation"
        )
    if invite_list is not None:
        if invite_list.suffix != ".csv":
            raise SystemExit("Wrong `invite_list` file extension. Supported extensions: `.csv`")

    iam_init_script(
        organisation_name=organisation_name,
        organisation_pk=organisation_pk,
        service_account=service_account,
        api_key=api_key,
        invite_list=invite_list,
        customization_url=customization_url,
    )


@cli.command(name="initialize")
def initialize() -> None:
    run_initialization()


if __name__ == "__main__":
    cli()
