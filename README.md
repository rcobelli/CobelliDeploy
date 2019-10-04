# Cobelli Deploy
My personal deployment automation script for iOS, Android, & Web projects

I have a number of projects and each project has a number of applications (ex: Client 1 has an iOS and an Android app, Client 2 has an iOS and a web app, etc). This is a simple and easy way to manage deploying updates for all of these different applications.

This will __not__ take the place of a standard CI/CD pipeline but is rather a wrapper around all the things you have to do to get your code into the pipeline.

## Setup
  - Place this script in you main development folder
    - Each project you work on is located in a sub-directory
    - Each of these sub-directories is a 3-character project code (must be DNS safe)
    - Each project directory has a sub-directory for each application (iOS, Android, etc)
      - These sub-directories must be titled with the `"parent directory name"_"application name"`
        - *Examples*
        - `abc`:
          - `config.ini`
          - `abc-ios`
          - `abc-android`
          - `abc-backend`
      - There must also be a `config.ini` located in each directory
          - The `config.ini` must have the following attributes
```
[abc]
title="Alpha Bravo Charlie"
root_dir="a_b_c"
link="https://link-to-download.com"
```

## Buffer
[Buffer](https://buffer.com) is a great tool for managing social media. A great way of posting to social media is to let people know that new versions of the app are available for download. To use this functionality, you'll have to create your own Buffer application and enter the config values at the top of the script.

### Backend
The script will do the following:
  1. _(If it's a PHP project)_ Run a [PHP linter](https://github.com/FriendsOfPHP/PHP-CS-Fixer)
  2. Ask if you'd like to tag this deployment
      - If you do, it will schedule postings with Buffer
  4. Create a commit
  5. Push to remote
      - Once it has been pushed to the remote, your standard CI/CD pipeline will take over

### Android
The script will do the following:
  1. Analyze the already created release APK
  2. Create a git commit using the version number _(ex: 5)_
  3. Create a tag with the version name _(ex: 1.2.3)_
  4. Push to remote
  5. Schedule postings with Buffer

### iOS
  1. Update [Fastlane](https://github.com/fastlane)
  2. (Optionally) Run [ImageOptim](https://imageoptim.com)
  3. (Optionally) Generate screenshots (using Fastlane)
  4. Download existing meta data from the App Store (using Fastlane)
  5. Ask for your change log (will be displayed on the App Store)
  6. Run your Fastlane lanes (either beta or release builds)
  7. Create a git commit using the version number _(ex: 5)_
  8. Create a tag with the version name _(ex: 1.2.3)_
  9. Push to remote
  10. Schedule postings with Buffer


## TODO
  - Add more documentation on Buffer
  - Add support for Mac applications
  - Build the signed APK for android directly from the CLI (maybe using fastlane)
