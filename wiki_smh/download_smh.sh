#!/bin/bash

# USAGE: download_stub-meta-history.sh <wiki-lang-code> <date>

# Initialise parameters
## Which dump?
wiki="$1wiki"
date="$2"

## Make download folder
path="$HOME/Data/stub-meta-history_$date"

if [ ! -d "$path" ]
then
	mkdir -p $path
fi

cd $path
pwd

# Make list of files to download

urlRoot="https://dumps.wikimedia.org/$wiki/$date/"

list="$path/list_$date.txt"

if [ ! -f $list ]
then 
    curl -s "$urlRoot" | 
    grep -oE "$wiki-$date-stub-meta-history[0-9]+.xml.gz" | 
    sort -u > "$list" 
fi

# Download files

## Prompt to continue
echo "$urlRoot" 
cat "$list" 

read -sr -n1 -p "Continue [y/n]?" REPLY

if [ ! $REPLY = "y" ]
then 
    printf "\nDownload aborted\n"
    exit 1
fi

## Download files

printf "\nDownload started:\n"
wget -bc -B "$urlRoot" -i "$list" 

