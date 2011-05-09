#!/bin/bash

verbose=false
clean=false
compile=false
objdep=false
exe=a.out
target_dir="current"

usage="\n$(basename ${0}) will build the target(s)\n\n"
usage="${usage}Options:\n -h help\n -v verbose\n -c make clean"
usage="${usage}\n -m run make\n -d make object dependency"
usage="${usage}\n -x binary name"
usage="${usage}\n -t target directory (${target_dir})\n"

# options
while getopts hvcmdx:t: o; do
  case "$o" in
    h) echo -e "${usage}"; exit 1;;
    v) verbose=true;;
    c) clean=true;;
    m) compile=true;;
    d) objdep=true;;
    x) exe=$OPTARG;;
    t) target_dir=$OPTARG;;
  esac
done
bin_dir="${target_dir}/bin"


if ${compile} ; then
  if ! test -d ${bin_dir} ; then
    mkdir ${bin_dir}
  fi
fi

# directory change
cd ..
target_dir="./build/${target_dir}"
bin_dir="${target_dir}/bin"

actions=""
if ${clean} ; then
  actions="CLEAN"
fi
if ${compile} ; then
  if test -n "${actions}" ; then
    actions="${actions} "
  fi
  actions="${actions}COMPILE"
fi

for am in ${target_dir}/*.arch.make ; do
  bin_name=${am%%.arch.make}
  bin_name=$(basename ${bin_name})
  bin_name="${bin_dir}/${bin_name}"

  ln -sf ${am} ./arch.make

  echo
  echo "[$actions] ${bin_name}"

  if ${verbose} ; then
    if ${clean} ; then
      make clean
    fi

    if ${compile} ; then
      if ${objdep} ; then
        make objdep
      fi
      make
    fi
  else
    if ${clean} ; then
      make clean  > ./${bin_name}.build.log
    fi

    if ${compile} ; then
      if ${objdep} ; then
        make objdep > ./${bin_name}.build.log
      fi
      make         >> ./${bin_name}.build.log
    fi
  fi

  if ${compile} ; then
    if test -x ./${exe} ; then
      mv -f ./${exe} ./${bin_name}
    else
      echo "Error compiling ${bin_name}"
    fi
  fi
  if ${clean} ; then
    rm -f ./arch.make
  fi
done
echo
