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
        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #5c5f5e;
            color: white;
            line-height: 1.6;
        }

        header {
            background-image: url('nekkuma.png');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            height: 60vh;
            min-height: 300px;
            max-height: 550px;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }

        h1 {
            margin: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: clamp(1.8rem, 4vw, 2.5rem);
            text-align: center;
            padding: 0 20px;
        }

        nav {
            margin: 20px;
            max-width: 1200px;
            margin: 20px auto;
            padding: 0 20px;
        }

        nav ul {
            list-style-type: none;
            padding: 0;
        }

        nav ul li {
            margin: 15px 0;
            padding: 10px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }

        nav ul li:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }

        nav ul li a {
            text-decoration: none;
            font-size: clamp(1rem, 2.5vw, 1.2rem);
            color: white;
            display: block;
            word-wrap: break-word;
            line-height: 1.4;
        }

        nav ul li a:hover {
            color: #007BFF;
        }

        /* Mobile styles */
        @media screen and (max-width: 768px) {
            header {
                height: 50vh;
                min-height: 250px;
            }

            h1 {
                font-size: clamp(1.5rem, 6vw, 2rem);
                margin: 15px;
            }

            nav {
                margin: 15px;
                padding: 0 15px;
            }

            nav ul li {
                margin: 10px 0;
                padding: 12px;
            }

            nav ul li a {
                font-size: clamp(0.9rem, 3.5vw, 1.1rem);
                line-height: 1.5;
            }
        }

        /* Small mobile styles */
        @media screen and (max-width: 480px) {
            header {
                min-height: 200px;
		background-position-x: 20%;
            }

            h1 {
                font-size: clamp(1.3rem, 7vw, 1.8rem);
                margin: 10px;
            }

            nav {
                margin: 10px;
                padding: 0 10px;
            }

            nav ul li {
                margin: 8px 0;
                padding: 10px;
            }

            nav ul li a {
                font-size: clamp(0.8rem, 4vw, 1rem);
            }
        }

        /* Large screen styles */
        @media screen and (min-width: 1200px) {
            nav {
                max-width: 1400px;
            }

            nav ul li a {
                font-size: 1.3rem;
            }
        }

        /* Ensure images don't overflow */
        img {
            max-width: 100%;
            height: auto;
        }

        /* Smooth scrolling */
        html {
            scroll-behavior: smooth;
        }
    </style>
<head>
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
                        pandoc -s -f odt "$odt_filename" --extract-media=. -o "$filename.html" --css="style.css"
			sed -i '/<style>/,/<\/style>/d' "$filename.html"
			sed -i 's|<body>|<body><div class="article-wrapper">|' "$filename.html"
			sed -i 's|</body>|</div></body>|' "$filename.html"
			cp ../style.css .
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
