#!/bin/sh

if [ "$#" -eq 1 ]
then
  if [ -d $1 ]
  then

    for f in ./$1/**/*.eps
    do
      echo "Processing $f"
      /usr/local/bin/epstopdf "$f"
    done

    find $1 \! -name '*.pdf' -delete

  else
    echo "Directory $1 does not exist"
    exit 1
  fi

else
  echo "Source directory not supplied"
  exit 1
fi
