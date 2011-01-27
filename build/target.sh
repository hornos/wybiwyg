#!/bin/bash

makes_dir="./makes"
targets_dir="./targets"

usage="\n$(basename ${0}) will create current as a target "
usage="${usage}for the build script.\n\n"
usage="${usage}Options:\n -h help\n -m directory for make files (${makes_dir})"
usage="${usage}\n -t target directory (${targets_dir})\n"

# options
while getopts hm:t: o; do
  case "$o" in
    h) echo -e ${usage}; exit 1;;
    m) makes_dir=$OPTARG;;
    t) targets_dir=$OPTARG;;
  esac
done

# menu
echo -e "\nTarget menu for the build\n"
dc=1
dl=()
for d in ${makes_dir}/* ; do
  if test -d ${d} ; then
    dbn=$(basename "${d}")
    dl[${dc}]="${dbn}"
    echo "${dc}. ${dbn}"
    dc=$((dc+1))
  fi
done
echo "q. Exit"

# target link
echo -en "\nChoose target: "
read t
echo "${t}" | grep "^[0-9]+$" &> /dev/null
_r=$?
if test $? -gt 0 ; then
  exit ${_r}
fi
dt=${dl[${t}]}

if test -z "${dt}" ; then
  exit ${_r}
fi

src="${makes_dir}/${dt}"
dst="${targets_dir}"
lnk="./current"
lnkdst="${dst}/${dt}"

if ! test -d "${lnkdst}" ; then
  mkdir -p "${lnkdst}"
fi
cp -f ${src}/* "${lnkdst}"

if test -L "${lnk}" ; then
  rm -f "${lnk}"
fi
ln -s "${lnkdst}" "${lnk}"
