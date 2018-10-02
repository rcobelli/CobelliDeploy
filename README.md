# Cobelli Deploy
My personal deployment automation script for iOS, Android, Mac & Web (LAMP) projects

## Setup
  - Place this script in you main development folder
    - Each project you work on is located in a sub-directory
    - Each of these sub-directories is a 3-character project code (must be DNS safe)
    - Each project directory has a sub-directory for each application (iOS, Android, etc)
      - These sub-directories must be titled with the "parent directory name"-"application name"
        - *Examples*
        - `ABC`:
          - `config.ini`
          - `abc-ios`
          - `abc-android`
          - `abc-backend`
          - `abc-mac`
      - There must also be a config.ini located in each directory
```
[abc]
title="Alpha Bravo Charlie"
root_dir="a_b_c"
```

### Backend
*This will only work with PHP code*
The script will do the following:
  1. Run a PHP linter
  2. Confirm that debug statements are turned off
  3. Ask if this is a major release
    - If it is, it will create a Trello ticket for PR purposes
  4. Create a git commit
  5. Push to remote 


### Android
The script will do the following:
  1. Analyze the already created release APK
  2. Create a git commit using the APK version code and version number
  3. Push to remote
  4. Create a Trello ticket for PR purposes

### iOS 
  1. Run a Fastlane lane
    - Only two lanes are supported (release and debug)
  2. *Release builds only* Prompt you to run ImageOptim
  3. Ask for change log
  4. Upload the change log to iTC
  5. Create a git commit using the build number, and change log
  6. Create a git tag for the version
  7. Push to remote
  8. Create a Trello ticket for PR purposes

### Mac
*TODO*
