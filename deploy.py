import getpass
import os
import configparser
import inquirer
import sys
import time
import json
import requests
import subprocess
from shutil import copyfile

def ios():
    # Check if it has fastlane setup
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
    os.system("echo '" + changeLog + "' > fastlane/metadata/en-US/release_notes.txt")

    # Update the acknowledgements file (if Settings.bundle exists)
    if answers['releaseType'] == 'release' and os.path.isdir("Settings.bundle"):
        copyfile("Pods/Target Support Files/Pods-" + projectCode + "/Pods-" + projectCode + "-acknowledgements.plist", "Settings.bundle/Acknowledgements.plist")

    # Run the correct lane
    os.system("bundle exec fastlane " + answers['releaseType'])

    # Get the version and build numbers
    buildNum = os.popen("agvtool what-version -terse").read()
    buildVers = os.popen("xcodebuild -showBuildSettings 2> /dev/null | grep MARKETING_VERSION | tr -d 'MARKETING_VERSION =' ").read()

    os.system("git add .")
    os.system("git commit -am '" + buildNum + ": " + changeLog + "'")
    os.system("git tag " + buildVers)
    os.system("git push")

def android():
    # Check if it has fastlane setup
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
    ]
    answers = inquirer.prompt(questions)

    # Update fastlane
    os.system("bundle update fastlane")

    if answers['imageOptim']:
        os.system("imageoptim '**/*.jpg '**/*.jpeg' '**/*.png'")

    os.system("rm -rf app/build/outputs/")

    # Run the correct lane
    os.system("bundle exec fastlane " + answers['releaseType'])

    versionName = os.popen("bundletool dump manifest --bundle app/release/app-release.aab --xpath /manifest/@android:versionName").read()
    versionNum = os.popen("bundletool dump manifest --bundle app/release/app-release.aab --xpath /manifest/@android:versionCode").read()

    os.system("git add .")
    os.system("git commit -am '" + str(versionNum) + ": " + str(changeLog) + "'")
    os.system("git tag " + versionName)
    os.system("git push")

def backend():
    subprocess.call(
        ["/usr/bin/open", "-W", "-n", "-a", "/Applications/SourceTree.app"]
    )
    os.exit(0)

# Init
configMaster = configparser.ConfigParser()

# Move to all projects dir
os.chdir("/Users/" + getpass.getuser() + "/Sites")

print("+-----------------------------------------------------------------+")
print("|                    Cobelli Deployment System                    |")
print("+------------------------------------------------------------------")

# Figure out if this is a Rybel or Personal project
questions = [
  inquirer.List('type',
                message="Select a type",
                choices=[tuple(("Personal", "personal")), tuple(("Rybel", "clients"))],
            ),
]
projectType = inquirer.prompt(questions)['type']
os.chdir(projectType)

# Loop through all directories in project folder
projects = []
for i in os.listdir('.'):
    if os.path.isdir(i):
        if projectType == "rybel":
            configMaster.read(i + "/config.ini")
            config = configMaster[i]

            title = config['title'].strip("\"")

            projects.append(title)
        else:
            projects.append(i)
projects.sort()

questions = [
  inquirer.List('project',
                message="Select a project",
                choices=projects,
            ),
]

# Save the selected project code
projectCode = inquirer.prompt(questions)['project']

# Move into that project's directory
os.chdir(projectCode)


# Loop through all directories in project folder
applications = []
if os.path.isdir("ios"):
    applications.append(tuple(("iOS", "ios")))
if os.path.isdir("android"):
    applications.append(tuple(("Android", "android")))
if os.path.isdir("backend"):
    applications.append(tuple(("Backend", "backend")))

if len(applications) == 0:
    questions = [
      inquirer.List('application',
                    message="Select application type",
                    choices=["ios", "backend", "android"],
                ),
    ]

    # Save the selected application code
    applicationCode = inquirer.prompt(questions)['application']
elif len(applications) == 1:
    applicationCode = applications[0][1]
else:
    questions = [
      inquirer.List('application',
                    message="Select an application",
                    choices=applications,
                ),
    ]

    # Save the selected application code
    applicationCode = inquirer.prompt(questions)['application']

print("-------------------------------------------------------------------")

if len(applications) > 0:
    # Move into that application's directory
    os.chdir(applicationCode)

if applicationCode == "ios":
    ios()
elif applicationCode == "android":
    android()
elif applicationCode == "backend":
    backend()
