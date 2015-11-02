#!/bin/sh

WHERE=$(cd `dirname ${0}` && pwd)
cd ${WHERE}

# Default value for VENV_PATH is bootstrap_venv
VENV_PATH=${1:-bootstrap_venv}
echo "Use VENV_PATH as '${VENV_PATH}'"

if [ -z "${VIRTUAL_ENV}" ]; then
    if ! [ -d "${VENV_PATH}" ]; then
        virtualenv-2.7 ${VENV_PATH}
    fi
    source ${VENV_PATH}/bin/activate
fi

pip install -r requirements
