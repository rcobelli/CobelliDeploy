import getpass
import os
import configparser
import inquirer
import sys
import subprocess
from shutil import copyfile


def exec(command):
    if (os.system(command) != 0):
        raise Exception(command + " did not complete successfully")


def ios():
    # Check if it has fastlane setup
    if not os.path.exists("fastlane/Fastfile"):
        sys.exit("Fastlane not installed")

    exec("git status")

    print("-------------------------------------------------------------------")
    # Ask for change log
    changeLog = input("Change Log: ")

    questions = [
        inquirer.List('releaseType',
                      message="What type of release is this?",
                      choices=[('Release', 'release'), ('Beta', 'beta')],
                      ),
        inquirer.Confirm('screenshots',
                         message="Do you want to generate screenshots?",
                         default=False),
    ]
    answers = inquirer.prompt(questions)

    # Update fastlane
    exec("gem update")
    exec("bundle update fastlane")

    if answers['screenshots']:
        exec("bundle exec fastlane snapshot update --force")
        exec("bundle exec fastlane snapshot")

    # Remove old build artifacts
    exec("rm -f *.dSYM.zip")
    exec("rm -f *.ipa")

    # Save the changelog as the release notes
    exec("echo '" + changeLog + "' > fastlane/metadata/en-US/release_notes.txt")

    # Update the acknowledgements file (if Settings.bundle exists)
    if answers['releaseType'] == 'release' and os.path.isdir("Settings.bundle"):
        copyfile("Pods/Target Support Files/Pods-" + projectCode + "/Pods-" +
                 projectCode + "-acknowledgements.plist", "Settings.bundle/Acknowledgements.plist")

    # Run the correct lane
    exec("bundle exec fastlane " + answers['releaseType'])

    # Get the version and build numbers
    buildNum = os.popen("agvtool what-version -terse").read()
    buildVers = os.popen(
        "xcodebuild -showBuildSettings 2> /dev/null | grep MARKETING_VERSION | tr -d 'MARKETING_VERSION =' ").read()

    exec("git add .")
    exec("git commit -am '" + buildNum + ": " + changeLog + "'")
    exec("git tag " + buildVers)
    exec("git push")


def android():
    # Check if it has fastlane setup
    if not os.path.exists("fastlane/Fastfile"):
        sys.exit("Fastlane not installed")

    exec("git status")

    print("-------------------------------------------------------------------")
    # Ask for change log
    changeLog = input("Change Log: ")

    questions = [
        inquirer.List('releaseType',
                      message="What type of release is this?",
                      choices=[('Release', 'release'), ('Beta', 'beta')],
                      ),
        inquirer.Confirm('screenshots',
                         message="Do you want to generate screenshots?",
                         default=False),
    ]
    answers = inquirer.prompt(questions)

    # Update fastlane
    exec("gem update")
    exec("bundle update fastlane")

    # Save the changelog as the release notes
    exec("echo '" + changeLog +
         "' > fastlane/metadata/android/en-US/changelogs/default.txt")

    if answers['screenshots']:
        exec("bundle exec fastlane build_and_screengrab")

    # Run the correct lane
    exec("bundle exec fastlane " + answers['releaseType'])

    versionName = os.popen(
        "bundletool dump manifest --bundle app/build/outputs/bundle/regularRelease/app-regular-release.aab --xpath /manifest/@android:versionName").read()
    versionNum = os.popen(
        "bundletool dump manifest --bundle app/build/outputs/bundle/regularRelease/app-regular-release.aab --xpath /manifest/@android:versionCode").read()

    exec("git add .")
    exec("git commit -am '" + str(versionNum) + ": " + str(changeLog) + "'")
    exec("git tag " + versionName)
    exec("git push")


def backend():
    subprocess.call(
        ["/usr/bin/open", "-W", "-n", "-a", "/Applications/SourceTree.app"]
    )


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
                  choices=[tuple(("Personal", "personal")),
                           tuple(("Rybel", "clients"))],
                  ),
]
projectType = inquirer.prompt(questions)['type']

if projectType == "clients":
    # Client projects use AWS CodeCommit and CLI creds for src access
    questions = [
        inquirer.Text('profile', message="What AWS profile should be used?"),
    ]
    awsProfile = inquirer.prompt(questions)['profile']
    exec ('aws sso login --profile ' + awsProfile)


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
