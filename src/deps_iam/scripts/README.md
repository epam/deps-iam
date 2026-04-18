# DEPS IAM init script

## Description
#### Script for initializing deps-iam service. Can create organisation, create service account in the organisation and invite users to the organisation.

If `--organisation_name` is provided then new organisation with this name will be created and service account will be added to this organisation.
If `--customization_url` is provided then this value will be used when creating new organisation and will be ignored if using existing organisation.
If `--organisation_pk` is provided then existing organisation with this pk will be used.
If this option is used then should provide `--api_key` of a service account with access to the organisation.
`--organisation_name` and `--organisation_pk` are mutually exclusive.
If `--service_account` is provided then new service account with this email will be created and added to the organisation.
New service account cant be created for an already existing organisation, so `--organisation_pk` and `--service_account` are mutually exclusive.
If `--api_key` is provided then existing service account will be used.
`--service_account` and `--api_key` are mutually exclusive.
If `--invite_list` is provided then all emails from this file will be invited to join the organisation.
File should be in `.csv` format with one `email` field name in headers row and contain valid emails.

`--invite_list` file content example:
```csv
email
1@epam.com
2@epam.com
3@epam.com
```


## Usage
Usage: `python -m deps_iam iam_init [--help] (--organisation_name TEXT | --organisation_pk TEXT) (--service_account TEXT | --api_key TEXT) [--invite_list FILE] [--customization_url TEXT]`


Note: `--organisation_name` and `--organisation_pk` are mutually exclusive.

Note: `--service_account` and `--api_key` are mutually exclusive.

Note: `--organisation_pk` and `--service_account` are mutually exclusive.

Note: If `--organisation_name` is not provided `--customization_url` will be ignored.

#### Options:
- `--organisation_name` TEXT - New organisation name
- `--organisation_pk` TEXT   - Existing organisation pk
- `--service_account` TEXT   - New service account email
- `--api_key` TEXT           - Existing service account API key
- `--invite_list` FILE       - `.csv` file with a list of emails to be invited
- `--customization_url` TEXT - Organisation customization url
- `--help`                   - Show help message and exit.
