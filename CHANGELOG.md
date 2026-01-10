# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-10

### Added
- Initial release of DorsalWatch integration
- Support for monitoring shark reports from DorsalWatch API
- Current Reports sensor with complete report data as attributes
- Latest Report sensor with most recent report details
- Configuration flow with country selection (Australia, Hawaii, USA, Reunion)
- Optional state/province filtering
- Configurable page size and time range
- Automatic data updates every 5 minutes

### Features
- **Current Reports Sensor**: Shows count of reports with all report data accessible via attributes
- **Latest Report Sensor**: Shows latest report timestamp with detailed report information
- **Multi-Country Support**: Australia, Hawaii, USA, and Reunion
- **Flexible Configuration**: Free-text state filtering, customizable page size and time range
- **Rich Data**: Complete access to all report fields including location, shark type, coordinates, and more