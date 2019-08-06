#!/bin/bash

# USAGE: bash -i xmlgz_2_csv.sh <xmlgz_list.txt> <n_head=10000> <n_tail=
# Requires wiki_dump_parser python packaged

# Find list of files to convert 
input=$1
n_head=${2:-100000}
n_tail=${3:-100000}

if [ ${input#*.} == "txt" ]
then 
    list="$input"
    if [ ! -f "$list" ]
    then 
        echo "$list cannot be found"
        exit 1
    else
        while IFS= read -r line
            do files+=("$line")
        done < "$list"
    fi
else
    files[0]="$input"
fi 

# Read list into array 

# Loop over each file -- unzip, parse to csv, delete xml

# unzip
# extract head of xml for cross-referencing
# use wiki_dump_parse to create csv
# delete xml file

for gzfile in ${files[@]}
do
    echo "Decompressing $gzfile"
    gzip -dk $gzfile
    xmlfile=${gzfile%.gz}
    
    echo "Extracting page elements from first $n_head lines into head_$xmlfile"
    head -n $n_head $xmlfile |
    sed -n '/<page>/,/<\/page>/p' > "head_$xmlfile"
    echo "Extracting last $n_tail lines into tail_$xmlfile"
    tail -n $n_tail $xmlfile > "tail_$xmlfile"

	echo "Parsing XML to CSV"
    python -m wiki_dump_parser "$xmlfile" > parser-log_${xmlfile%.*}

    if [ -f ${xmlfile/%.xml/.csv} ]
	then 
        echo "Removing $xmlfile"
        rm "$xmlfile"
    else
		echo "Error parsing $xmlfile. Exiting loop"
		exit 3
    fi
done
