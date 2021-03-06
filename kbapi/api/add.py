# -*- encoding: utf-8 -*-
# kb-api v0.1.0
# A REST API for kb - the minimalist knowledge base organizer
# Copyright © 2020, alshapton.
# See /LICENSE for licensing information.

"""
kb-api add api module

:Copyright: © 2020, alshapton.
:License: GPLv3 (see /LICENSE).
"""


import os
from pathlib import Path
from typing import Dict

from kb.actions.add import add_artifact
from .constants import MIME_TYPE
import kb.db as db

# Use the flask framework
from flask import make_response
from werkzeug.utils import secure_filename


def add(args: Dict[str, str], config: Dict[str, str], file):
    """
    Adds a list of artifacts to the knowledge base of kb.

    Arguments:
    args:           - a dictionary containing the following fields:
                      file -> a list of files to add to kb
                      title -> the title assigned to the artifact(s)
                      category -> the category assigned to the artifact(s)
                      tags -> the tags assigned to the artifact(s)
                      author -> the author to assign to the artifact
                      status -> the status to assign to the artifact
    config:         - a configuration dictionary containing at least
                      the following keys:
                      PATH_KB_DB        - the database path of KB
                      PATH_KB_DATA      - the data directory of KB
                      EDITOR            - the editor program to call
    """

    # If there is a file to add.....

    if file:
        # Create "category" directory if it does not exist
        category_path = Path(config["PATH_KB_DATA"], args["category"])
        category_path.mkdir(parents=True, exist_ok=True)

        # Get the filename
        filename = secure_filename(file.filename)
        category_path = Path(config["PATH_KB_DATA"], args["category"])
        file.save(os.path.join(category_path, filename))
        os.rename(os.path.join(category_path, filename), os.path.join(category_path, args["title"]))

    conn = db.create_connection(config["PATH_KB_DB"])

    result = add_artifact(conn, args, config)
    conn.commit()

    if result is None:
        resp = make_response(({'Error': 'There was an issue adding the artifact'}), 200)
        resp.mimetype = MIME_TYPE['json']
        return (resp)

    if result > 1:
        resp = make_response(({'Added': result}), 200)

    if result <= 0:
        resp = make_response(({'Error': 'There was an issue adding the artifact - ' + result}), 200)

    resp.mimetype = MIME_TYPE['json']
    return (resp)
