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

# Get current date in YYYYMMDD format
current_date=$(date +%Y%m%d)
echo "Current date: $current_date"

# Delete existing html files
find -type f -name "*.html" -delete
ls -al

# Start of the HTML content
cat <<EOF > index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nekkuma</title>

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="Blog">
    <meta property="og:url" content="https://vagrantin.github.io/blog/">
    <meta property="og:title" content="Nekkuma">
    <meta property="og:description" content="BloguiBoulga">
    <meta property="og:image" content="https://vagrantin.github.io/blog/nekkuma.png">

    <!-- Twitter -->
    <meta property="twitter:card" content="BloguiBoulga">
    <meta property="twitter:url" content="https://vagrantin.github.io/blog/">
    <meta property="twitter:title" content="Nekkuma">
    <meta property="twitter:description" content="BloguiBoulga">
    <meta property="twitter:image" content="https://vagrantin.github.io/blog/nekkuma.png">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BloguiBoulga</title>
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
        <h1>Dump! Dump! Dump!</h1>
    </div>
    <nav>
        <ul>
EOF

# Create a temporary file to store entries with dates for sorting
temp_file=$(mktemp)

# Loop through each item in the current directory
for item in *; do
    # Check if the item is a directory
    if [ -d "$item" ]; then
        # Check if the directory name consists only of digits
        if echo "$item" | grep -q '^[0-9]\+$'; then
            # Check if the directory name is 8 digits (YYYYMMDD format)
            if [ ${#item} -eq 8 ]; then
                # Compare the directory date with current date
                if [ "$item" -le "$current_date" ]; then
                    echo "Processing article: $item (published - date reached)"

                    # Look for an HTML file in the directory
                    html_file=$(find "$item" -maxdepth 1 -type f -name "*.html" | head -n 1)
                    # Look for an ODT file in the directory
                    odt_file=$(find "$item" -maxdepth 1 -type f -name "*.odt" | head -n 1)

                    # If HTML doesn't exist and ODT does, create the HTML version with media
                    if [ -z "$html_file" ] && [ -n "$odt_file" ]; then
                        odt_filename=$(basename "$odt_file")
                        filename=${odt_filename%.*}

                        # Navigate into the date directory to run pandoc
                        # This ensures media extraction paths are relative to the ODT file
                        # and the output HTML is placed correctly within "$item".
                        cd "$item" || exit # Exit if cd fails
                        pandoc -s -f odt "$odt_filename" --extract-media=. -o "$filename.html" --css="../style.css"
                        cd .. # Navigate back to the original directory
                    fi

                    # Extract the year, month, and day parts from the directory name
                    year=$(echo "$item" | cut -c1-4)
                    month=$(echo "$item" | cut -c5-6)
                    day=$(echo "$item" | cut -c7-8)

                    # Convert the directory name to the desired date format
                    month_name=$(date -d "${year}-${month}-${day}" "+%B")
                    day_ordinal=$(convert_to_ordinal "$day")

                    # Re-check for the HTML file after potential creation
                    html_file=$(find "$item" -maxdepth 1 -type f -name "*.html" | head -n 1)
                    # If no HTML file is found, default to 404.html (or handle as appropriate)
                    if [ -z "$html_file" ]; then
                        html_file="$item/404.html" # Assuming a 404.html might exist in the date folder
                    fi

                    # Extract just the filename from the path
                    html_filename=$(basename "$html_file")

                    # Determine the base filename of the ODT file for title lookup
                    odt_base_filename=""
                    if [ -n "$odt_file" ]; then # Ensure an ODT file was actually found
                        odt_filename_full_path=$(find "$item" -maxdepth 1 -type f -name "*.odt" | head -n 1)
                        odt_base_filename=$(basename "${odt_filename_full_path%.*}")
                    fi

                    # Get the title from the corresponding text file in titlesOfTheMonth/
                    article_title=""
                    if [ -n "$odt_base_filename" ]; then # Only try to get title if an ODT base filename exists
                        title_file="titlesOfTheMonth/${odt_base_filename}.txt"
                        if [ -f "$title_file" ]; then
                            article_title=$(head -n 1 "$title_file")
                        fi
                    fi

                    # Create the list item entry
                    if [ -n "$article_title" ]; then
                        entry="            <li><a href=\"$item/$html_filename\">$month_name ${day_ordinal}, $year - $article_title</a></li>"
                    else
                        entry="            <li><a href=\"$item/$html_filename\">$month_name ${day_ordinal}, $year</a></li>"
                    fi

                    # Add to temp file with date for sorting (most recent first)
                    echo "$item|$entry" >> "$temp_file"
                else
                    echo "Skipping article: $item (not yet published - date not reached)"
                fi
            else
                echo "Skipping directory: $item (not in YYYYMMDD format)"
            fi
        fi
    fi
done

# Sort entries by date (descending - most recent first) and add to HTML
sort -t'|' -k1,1nr "$temp_file" | cut -d'|' -f2- >> index.html

# Clean up temp file
rm "$temp_file"

# End of the HTML content
cat <<EOF >> index.html
        </ul>
    </nav>
</body>
</html>
EOF

echo "Build complete! Articles published up to: $current_date"
ls -al
