import getpass
import os
import configparser
import inquirer
import sys
import time
import json
import requests

# BUFFER CONFIG VARIABLES
access_token = ""
facebook_id = ""
twitter_id = ""

def postToBuffer(version, changeLog):
    product = projects[projectCode]['title']
    link = projects[projectCode]['link']

    task = {"profile_ids[]": facebook_id, "shorten": "false", "attachment": "false", "text": "We are rolling out version " + version + " of " + product + ". Download " + product + " at " + link + "! \n\nChange Log:\n" + changeLog }
    requests.post('https://api.bufferapp.com/1/updates/create.json?access_token=' + access_token, data=task)

    task = {"profile_ids[]": twitter_id, "shorten": "false", "attachment": "false", "text": "We are rolling out version " + version + " of " + product + ". Download " + product + " at " + link + "! \n\nChange Log:\n" + changeLog }
    requests.post('https://api.bufferapp.com/1/updates/create.json?access_token=' + access_token, data=task)



def ios():
    # Check if has fastlane setup
    if not os.path.exists("fastlane/Fastfile"):
        sys.exit("Fastlane not installed")

    os.system("git status")

    print("-------------------------------------------------------------------")
    # Ask for change log
    changeLog = input("Change Log: ")

    questions = [
        inquirer.List('releaseType',
                      message="What type of release is this?",
                      choices=[('Release', 'release'), ('Beta', 'beta')],
                  ),
        inquirer.Confirm('imageOptim',
                         message="Do you want to run ImageOptim?" ,
                         default=False),
        inquirer.Confirm('screenshots',
                         message="Do you want to generate screenshots?" ,
                         default=False),
    ]
    answers = inquirer.prompt(questions)

    # Update fastlane
    os.system("bundle update fastlane")

    if answers['imageOptim']:
        os.system("imageoptim '**/*.jpg '**/*.jpeg' '**/*.png'")

    if answers['screenshots']:
        os.system("bundle exec fastlane snapshot update --force")
        os.system("bundle exec fastlane snapshot")

    # Remove old build artifacts
    os.system("rm -f *.dSYM.zip")
    os.system("rm -f *.ipa")

    # Download existing metadata from the store
    os.system("bundle exec fastlane deliver download_metadata -force")

    # Save the changelog as the release notes
    os.system(changeLog + " > fastlane/metadata/en-US/release_notes.txt")

    # Run the correct lane
    os.system("bundle exec fastlane " + answers['releaseType'])

    # Get the version and build numbers
    buildNum = os.popen("agvtool what-version -terse").read()
    buildVers = os.popen("agvtool what-marketing-version -terse1 | sed -n 2p").read()

    os.system("git add .")
    os.system("git commit -am '" + buildNum + ": " + changeLog + "'")
    os.system("git tag " + buildVers)
    os.system("git push --tags")

    # Add a new social media post
    postToBuffer(buildVers, changeLog)

def android():
    # TODO: Build the signed APK with gradle

    # Get the version number and name
    with open('app/release/output.json', 'r') as tmpFile:
        gradleOutput=tmpFile.read()

    gradleOutput = json.loads(gradleOutput)

    # Version code (like 5)
    buildNum = gradleOutput[0]["apkData"]["versionCode"]
    # Version number (like 1.2.3)
    buildVers = gradleOutput[0]["apkData"]["versionName"]
    os.system("git status")

    print("-------------------------------------------------------------------")
    # Ask for change log
    changeLog = input("Change Log: ")

    os.system("git add .")
    os.system("git commit -am '" + buildNum + ": " + changeLog + "'")
    os.system("git tag " + buildVers)
    os.system("git push --tags")

    # Add a new social media post
    postToBuffer(buildVers, changeLog)

def backend():
    # Check if it's a PHP project
    if os.path.exists(".php_cs.dist"):
        # Run PHPLint
        os.system("php-cs-fixer fix --show-progress=estimating")
        print("-------------------------------------------------------------------")

    os.system("git status")

    print("-------------------------------------------------------------------")
    # Ask for change log
    changeLog = input("Change Log: ")

    os.system("git add .")
    os.system("git commit -am '" + changeLog + "'")

    # Ask if you want to tag
    confirm = {
        inquirer.Confirm('confirmed',
                         message="Do you want to add a new tag?" ,
                         default=False),
    }

    print("-------------------------------------------------------------------")

    if inquirer.prompt(confirm)["confirmed"]:
        # Show current tag
        print("Most recent tag: ", end="\r")
        os.system("git describe --abbrev=0 --tags")

        print("-------------------------------------------------------------------")
        # Ask for new tag
        newTag = input("New tag: ")
        os.system("git tag " + newTag)

        # Add a new social media post
        postToBuffer(newTag, changeLog)

    os.system("git push --tags")

# Init
configMaster = configparser.ConfigParser()

# Move to all projects dir
os.chdir("/Users/" + getpass.getuser() + "/Sites")

print("+-----------------------------------------------------------------+")
print("|                    Cobelli Deployment System                    |")
print("+------------------------------------------------------------------")

projects = {}
projectCodes = []

# Loop through all directories in project folder
for i in os.listdir('.'):
    if os.path.isdir(i):
        configMaster.read(i + "/config.ini")
        config = configMaster[i]

        try:
            title = config['title'].strip("\"")
            link = config['link'].strip("\"")
        except:
            link = False

        projects.update({ i: {
            "title": title,
            "link" : link
        }})

        projectCodes.append(tuple((title, i)))

questions = [
  inquirer.List('project',
                message="Select which project to deploy?",
                choices=projectCodes,
            ),
]

# Save the selected project code
projectCode = inquirer.prompt(questions)['project']

# Move into that project's directory
os.chdir(projectCode)

applications = []

# Loop through all directories in project folder
if os.path.isdir(projectCode + "_ios"):
    applications.append(tuple(("iOS", "ios")))
if os.path.isdir(projectCode + "_android"):
    applications.append(tuple(("Android", "android")))
if os.path.isdir(projectCode + "_backend"):
    applications.append(tuple(("Backend", "backend")))

applications.sort(key=lambda tup: tup[0])

if len(applications) == 0:
    sys.exit("No applications found for this project")
elif len(applications) == 1:
    applicationCode = applications[0][1]
else:
    questions = [
      inquirer.List('application',
                    message="Select which application to deploy?",
                    choices=applications,
                ),
    ]

    # Save the selected application code
    applicationCode = inquirer.prompt(questions)['application']

# Move into that application's directory
os.chdir("./" + projectCode + "_" + applicationCode)

print("-------------------------------------------------------------------")

if applicationCode == "ios":
    ios()
elif applicationCode == "android":
    android()
elif applicationCode == "backend":
    backend()
