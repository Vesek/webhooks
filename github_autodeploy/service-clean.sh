#/bin/bash
SCRIPTPATH=$(dirname $(realpath $0))
USER=$(id -un)

sed -e "s|$SCRIPTPATH|<PWD>|g" -e "s|$USER|<USER>|g"
