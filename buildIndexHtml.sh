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

# Start of the HTML content
cat <<EOF > index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Simple Blog</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
	    background-color:#5c5f5e;
            color: white;
        }
        header {
            background-image: url('nekkuma.png'); /* Replace with your image path */
            background-size: cover;
            background-position: center;
            height: 550px;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        h1 {
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 2.5em;
        }
        nav {
            margin: 20px;
        }
        nav ul {
            list-style-type: none;
            padding: 0;
        }
        nav ul li {
            margin: 10px 0;
        }
        nav ul li a {
            text-decoration: none;
            font-size: 1.2em;
            color: white;
        }
        nav ul li a:hover {
            color: #007BFF;
        }
    </style>
</head>
<body>
    <header>
    </header>
    <div>
        <h1>Welcome to My Blog</h1>
    </div>
    <nav>
        <ul>
EOF

# Delete existing html files
find -type f -name "*.html" -delete
ls -al

# Loop through each item in the current directory
for item in *; do
    # Check if the item is a directory
    if [ -d "$item" ]; then
        # Check if the directory name consists only of digits
        if echo "$item" | grep -q '^[0-9]\+$'; then
	    # look for an html file in the directory
            html_file=$(find "$item" -maxdepth 1 -type f -name "*.html" | head -n 1)
            # Look for an ODT file in the directory
            odt_file=$(find "$item" -maxdepth 1 -type f -name "*.odt" | head -n 1)
	    # if html don't exist and the odt exist create the html version with media
	    #echo "html_file: $html_file"
	    #echo "odt_file: $odt_file"
            if [ -z "$html_file" ] && [ -n "$odt_file" ]; then
            	odt_file=$(find "$item" -maxdepth 1 -type f -name "*.odt" | head -n 1)
		odt_filename=$(basename "$odt_file")
		#echo $odt_filename
		filename=${odt_filename%.*}
		cd $item
		pandoc -s -f odt "$odt_filename" --extract-media=. -o "$filename.html" --css="../style.css"
		cd ..

            fi
            # Extract the year, month, and day parts from the directory name
            year=$(echo "$item" | cut -c1-4)
            month=$(echo "$item" | cut -c5-6)
            day=$(echo "$item" | cut -c7-8)

            # Convert the directory name to the desired date format
            month_name=$(date -d "${year}-${month}-${day}" "+%B")
            day_ordinal=$(convert_to_ordinal "$day")

	    # look for an html file in the directory
            html_file=$(find "$item" -maxdepth 1 -type f -name "*.html" | head -n 1)
            # If no HTML file is found, default to 404.html
            if [ -z "$html_file" ]; then
                html_file="$item/404.html"
            fi

            # Extract just the filename from the path
            html_filename=$(basename "$html_file")

            # Append the formatted date as a list item to the HTML file
            echo "            <li><a href=\"$item/$html_filename\">$month_name ${day_ordinal}, $year</a></li>" >> index.html
        fi
    fi
done

# End of the HTML content
cat <<EOF >> index.html
        </ul>
    </nav>
</body>
</html>
EOF

