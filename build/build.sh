#!/bin/bash

verbose=false
clean=false
compile=false
objdep=false
exe=a.out
bindir="./bin"

while getopts vcmdx: o; do
  case "$o" in
    v) verbose=true;;
    c) clean=true;;
    m) compile=true;;
    d) objdep=true;;
    x) exe=$OPTARG;;
  esac
done


if ${compile} ; then
  if ! test -d ${bindir} ; then
    mkdir ${bindir}
  fi
fi

cd ..

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

for am in ./build/*.arch.make ; do
  bin_name=${am%%.arch.make}
  bin_name=$(basename ${bin_name})
  bin_name="build/bin/${bin_name}"

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
