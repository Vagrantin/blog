#!/bin/sh

# Copy the python script that will be execute remotely
scp odt-rag-create-title.py ai:~/devouille/otoTitle

# Clean up odt files on the target machine
ssh ai "cd ~/devouille/otoTitle/source/ && rm *.odt"

# Copy odt file to Ai machine for title creation
find -type f -name "*.odt" -exec scp {} ai:~/devouille/otoTitle/source/ \;

# Remote exec the python script for title creation
ssh ai "cd ~/devouille/otoTitle/ && source ~/devouille/otoTitle/langchain-env/bin/activate && python ~/devouille/otoTitle/odt-rag-create-title.py"

# Download the outputs provided by the python script
scp ai:~/devouille/otoTitle/output/*.txt titlesOfTheMonth/
