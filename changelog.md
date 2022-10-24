# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## [git] - 2021-08-03
### Added
- Add missing wav files.

### Fixed
- Change to relative imports (Now the game runs on Python 3.9.2).
- (effect.py) Use PEP8 more.

## [git] - 2021-08-03
### Added
- Add mouse support for menus and action.
- Save screenshots in ~/Pictures or ~/Pictures/Screenshots if exists and date the filename.


## [git] - 2021-08-01
### Changed
- Change jump from 'up' to 'space'

### Added
- Use a gamepad or joystick along with keys (using the MIT Licensed SoftController module: src/controller.py from [github.com/poikilos/SoftController](https://github.com/poikilos/SoftController)).
  - See controls.py for easy remapping or adding more.
  - add "ad" keys move left and right.


## [git https://github.com/poikilos/lepidopterist/commit/d92e63b6bf8932c29066cd94315f806597f33cfd] -
(committed 2021-07-29)
### Added
- Save some general score statistics in a conf-style format such as for LAN contests.

### Changed
- Prevent easy mode such as for LAN contests.
  - Check a new global in main.py: `enable_easy` :edit: **later changed to `enable_easy_shortcut` which prevents all cheat sequences**
