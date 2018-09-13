#! /bin/bash

# Setup color variables
red=`tput setaf 1`
green=`tput setaf 2`
blue=`tput setaf 6`
bold=`tput bold`
reset=`tput sgr0`

# Find the working directory
dir=$(dirname "$0")

# Header
echo "+-----------------------------------------------------------------+"
echo "|                    ${bold}Cobelli Deployment System${reset}                    |"
echo "+-------+----------------------------------------------------------"

# Loop through everything in the sites directory
count=1
for file in ${dir}/*; do
	if ! [ ! -f $file"/"config.ini ]; then
		# Check if the "file" is a directory
		# Ensure the directory has a config.ini
		# Pull the `title` attribute from the config.ini
		# Display it
		echo -e "|  "$count"\t|"$(awk -F "=" '/title/ {print $2}' $file/config.ini) | tr -d '"'
	fi
	count=$((count + 1))
done

echo "+-------+----------------------------------------------------------"

# Ask for the project number
read -p "${blue}Which project?${reset} " project

# Start the count again but save the requested path as extension
count=1
extension="___EMPTY___"
for file in ${dir}/*; do
	if [ "$count" -eq "$project" ]; then
		extension=$(basename "$file")
	fi
	count=$((count + 1))
done

# Validate there is a project for this number
if [ "$extension" = "___EMPTY___" ]; then
	echo "                    ${red}Invalid input"
	read asdfasdf
	exit 0
fi

# Navigate into the requested dir
cd ${dir}/$extension

echo "+-------+----------------------------------------------------------"

# Check which applications exist for this project
if [ -d ${dir}/$extension"/"$extension"_backend/" ]; then
	echo -e "|  1\t|Backend"
fi

if [ -d ${dir}/$extension"/"$extension"_android/" ]; then
	echo -e "|  2\t|Android"
fi

if [ -d ${dir}/$extension"/"$extension"_ios/" ]; then
	echo -e "|  3\t|iOS"
fi

if [ -d ${dir}/$extension"/"$extension"_mac/" ]; then
	echo -e "|  4\t|Mac"
fi
echo "+-------+----------------------------------------------------------"

# Ask for the application number
read -p "${blue}Which application?${reset} " application

echo "-------------------------------------------------------------------"

if [ "$application" -eq "1" ]; then
	# Backend
	if ! [ -d ${dir}/$extension"/"$extension"_backend/" ]; then
		echo "                    ${red}Invalid input"
		read asdfasdf
		exit 0
	fi

	cd ${dir}/$extension/$extension"_backend"

	# Run a PHP linter
	echo "Checking PHP..."
	eval 'php-cs-fixer fix --verbose --show-progress=estimating'

	echo "-------------------------------------------------------------------"
	read -p "${blue}Is error repoting disabled? (Y/N)${reset} " errorChecking


	if [ "$errorChecking" = "N"]; then
		# Wrap it up
		echo "-------------------------------------------------------------------"
		echo "                    ${red}Go disable error reporting"
		read asdfasdf
		exit 0
	fi

	# Ask for the git commit message
	eval "git status"
	echo "-------------------------------------------------------------------"
	read -p "${blue}Change Log:${reset} " message

	# Handle the git stuff
	eval "git add ."
	eval "git commit -a -m '"$message"'"
	eval "git push"

	# Wrap it up
	echo "-------------------------------------------------------------------"
	echo "                    ${green}Done!"
	read asdfasdf
	exit 0
elif [ "$application" -eq "2" ]; then
	# Android

	# Check if an android application actually exists for this project
	if ! [ -d ${dir}/$extension"/"$extension"_android/" ]; then
		echo "-------------------------------------------------------------------"
		echo "                    ${red}Invalid input"
		read asdfasdf
		exit 0
	fi

	# Navigate into where the signed APK is
	cd ${dir}/$extension/$extension"_android/app/release"

	# Extract build info
	buildNum="$(cat output.json | jq '.[0]["apkInfo"]["versionCode"]')" # Version code (like 5)
	buildVers="$(cat output.json | jq '.[0]["apkInfo"]["versionName"]')" # Version number (like 1.2.3)

	# Return to working direcotry
	cd ${dir}/$extension/$extension"_android"

	# Ask for the git commit message
	eval "git status"
	echo "-------------------------------------------------------------------"
	read -p "${blue}Change Log:${reset} " message

	# Handle the git stuff
	eval "git add ."
	eval "git commit -a -m '"$buildNum": "$message"'"
	eval "git tag $buildVers"
	eval "git push"
	eval "git push --tags"

	# Create a trello ticket to remind me to write an update blog post
	eval "trello \"Write blog for $extension\""

	# Wrap it up
	echo "-------------------------------------------------------------------"
	echo "                          ${green}Done!"
	read asdfasdf
	exit 0
elif [ "$application" -eq "3" ]; then
	# iOS

	# Check that an iOS Application exists for the project
	if ! [ -d ${dir}/$extension"/"$extension"_ios/" ]; then
		echo "-------------------------------------------------------------------"
		echo "                    ${red}Invalid input"
		read asdfasdf
		exit 0
	fi

	# Check if Fastlane is installed
	if [ ! -f ${dir}/$extension/$extension"_ios/fastlane/"Fastfile ]; then
		echo "                          ${red}Fastlane Not Installed"
		read asdfasd
		exit 0
	fi

	# Ask if this is a beta or release build
	# This determines which lane is run
	read -p "${blue}Is this a (B)eta or (R)elease build?${reset} " buildType

	echo "-------------------------------------------------------------------"

	# Release builds only
	if [ "$buildType" = "R" ]; then
		# Prompt if the user wants to run imageoptim
		read -p "${blue}Do you want to run ImageOptim? (Y/N)${reset} " ioDecision

		if [ "$ioDecision" = "Y" ]; then
			# Move into the specified directory where all the assets are
			# The directory is specified as the `root_dir` attribute of the config.ini
			cd ${dir}/$extension/$extension"_ios"/$(awk -F "=" '/root_dir/ {print $2}' ${dir}/$extension/config.ini | tr -d \" | tr -d \ )/

			# Run imageoptim on all images in asset folder for release builds
			eval "imageoptim '**/*.jpg' '**/*.jpeg' '**/*.png'"
		fi
	fi

	# Move back out to where it can find fastlane
	cd ${dir}/$extension/$extension"_ios"

	# Download the most current metadata from iTC
	eval "bundle exec fastlane deliver download_metadata -force"

	# Ask for the git commit message
	eval "git status"
	echo "-------------------------------------------------------------------"
	read -p "${blue}Change Log:${reset} " message

	# Save the git change log into the release notes to be uploaded back to iTC
	echo $message > ${dir}/$extension/$extension"_ios/fastlane/metadata/en-US/release_notes.txt"

	if [ "$buildType" = "B" ]; then
		eval "bundle exec fastlane beta"
	else
		eval "bundle exec fastlane release"
	fi

	buildNum="$(xcrun agvtool vers -terse)" # Build number (like 180512)
	buildVers="$(xcrun agvtool mvers -terse1)" # Version number (like 1.2.3)

	# Handle the git stuff
	eval "git add ."
	eval "git commit -a -m '"$buildNum": "$message"'"
	eval "git tag $buildVers"
	eval "git push"
	eval "git push --tags"

	# Create a trello ticket to remind me to write an update blog post
	if [ "$buildType" = "R" ]; then
		eval "trello \"Write blog for $extension\""
	fi

	# Wrap it up
	echo "-------------------------------------------------------------------"
	echo "                          ${green}Done!"
	read asdfasdf
	exit 0
elif [ "$application" -eq "4" ]; then
	# Mac

	# TODO Implement this
	echo "                    ${red}Mac currently isn't supported"
	read asdfasdf
	exit 0
else
	# Some other number

	echo "                    ${red}Invalid input"
	read asdfasdf
	exit 0
fi
