#!/bin/sh

# Function to convert day number to ordinal form
convert_to_ordinal() {
    day=$1
    case $day in
        01 | 21 | 31) echo "${day}st" ;;
        02 | 22) echo "${day}nd" ;;
        03 | 23) echo "${day}rd" ;;
        *) echo "${day}th" ;;
    esac
}

# Loop through each item in the current directory
for item in *; do
    # Check if the item is a directory
    if [ -d "$item" ]; then
        # Check if the directory name consists only of digits
        if echo "$item" | grep -q '^[0-9]\+$'; then
            # Extract the year, month, and day parts from the directory name
            year=$(echo "$item" | cut -c1-4)
            month=$(echo "$item" | cut -c5-6)
            day=$(echo "$item" | cut -c7-8)

            # Convert the directory name to the desired date format
            month_name=$(date -d "${year}-${month}-${day}" "+%B")
            day_ordinal=$(convert_to_ordinal "$day")

            # Output the formatted date
            echo "Directory: $item -> Converted Date: $month_name ${day_ordinal}, $year"
        fi
    fi
done

