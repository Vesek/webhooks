#/bin/bash
SCRIPTPATH=$(dirname $(realpath $0))
USER=$(id -un)

sed -e "s|<PWD>|$SCRIPTPATH|g" -e "s|<USER>|$USER|g"
