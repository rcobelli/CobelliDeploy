# Cobelli Deploy
My personal deployment automation script for iOS, Android, & Web projects

I have a number of projects and each project has a number of applications (ex: Client 1 has an iOS and an Android app, Client 2 has an iOS and a web app, etc). This is a simple and easy way to manage deploying updates for all of these different applications.

This will __not__ take the place of a standard CI/CD pipeline but is rather a wrapper around all the things you have to do to get your code into the pipeline.

## Setup
  - Place this script in you main development folder
    - Sort projects into either a `personal` or `clients` subdirectory
    - If projects have multiple components (say an iOS and Android app), create a subdirectory for each application (ex: backend, android, or ios)
    - If a project is a single component, place the source directly in this folder
    - __Example File Structure__
      - `/Users/ryan/Development/`
        - `clients`
          - `abc`:
            - `config.ini`
            - `abc-ios`
            - `abc-android`
            - `abc-backend`
        - `personal`
          - `xyz`
  - There must also be a `config.ini` located in each directory
      - The `config.ini` must have the following attributes
```
[abc]
title="Alpha Bravo Charlie"
root_dir="a_b_c"
link="https://link-to-download.com"
```

### Backend
The script will simply open SourceTree

### Android
  1. Update [Fastlane](https://github.com/fastlane)
  2. (Optionally) Run [ImageOptim](https://imageoptim.com)
  3. Run your Fastlane lanes (either beta or release builds)
  4. Create a git commit using the version number _(ex: 5)_
  5. Create a tag with the version name _(ex: 1.2.3)_
  6. Push to remote

### iOS
  1. Update [Fastlane](https://github.com/fastlane)
  2. (Optionally) Run [ImageOptim](https://imageoptim.com)
  3. (Optionally) Generate screenshots (using Fastlane)
  4. (Optionally) Update the `acknowledgements.plist` in `Settings.bundle` (from CocoaPods)
  5. Download existing meta data from the App Store (using Fastlane)
  6. Ask for your change log (will be displayed on the App Store)
  7. Run your Fastlane lanes (either beta or release builds)
  8. Create a git commit using the version number _(ex: 5)_
  9. Create a tag with the version name _(ex: 1.2.3)_
  10. Push to remote


## TODO
  - Add support for Mac applications
