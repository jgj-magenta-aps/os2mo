#!/bin/sh -e

DIR=$(cd $(dirname $0); pwd)
VENV="$DIR"/venv

if ! test -d "$VENV"
then
    echo "Creating virtual environment!" >&2

    python3 -m venv "$VENV"

    "$VENV"/bin/pip install -qU packaging pip setuptools wheel
    "$VENV"/bin/pip install -qr "$DIR"/requirements-test.txt
    "$VENV"/bin/pip install -qe "$DIR"
fi

# we also have '$VENV/bin/python', but use python -m so that we can
# override the program name

export FLASK_ENV=development
export FLASK_APP=mora.app:app

exec "$VENV"/bin/flask "$@"
