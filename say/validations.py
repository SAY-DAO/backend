import re


# TODO: Check the pattern with parsa and neda
USERNAME_PATTERN = r'^[a-zA-Z0-9_.]{4,12}$'
username_validator = re.compile(USERNAME_PATTERN).match

