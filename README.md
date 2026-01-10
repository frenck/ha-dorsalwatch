# DorsalWatch Home Assistant Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

A custom Home Assistant integration for monitoring shark reports from the DorsalWatch API.

## Installation

### HACS (Recommended)

1. Make sure that [HACS](https://hacs.xyz/) is installed
2. Go to HACS → Integrations
3. Click the three dots menu and select "Custom repositories"  
4. Add this repository URL: `https://github.com/your_github_username/ha-dorsalwatch`
5. Select "Integration" as the category
6. Click "Add"
7. Search for "DorsalWatch" in HACS and install it
8. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/dorsalwatch` folder to your Home Assistant `custom_components` directory.

2. Restart Home Assistant.

3. Go to Configuration > Integrations.

4. Click the "+" button to add a new integration.

5. Search for "DorsalWatch" and select it.

6. Enter your configuration:
   - **Country**: Select your country (Australia, Hawaii, USA, Reunion)
   - **Public Key**: Your DorsalWatch API public key (`ab61cd9427bea80f22e641c04c312195`)
   - **State** (optional): Specific state/province to filter reports (free text)
   - **Page Size**: Number of reports to fetch (default: 12)
   - **Time Range**: Days to look back (0 for all time)

## Sensors

The integration provides two sensors and geo-location entities for map display:

### DorsalWatch Current Reports
- Shows the total number of current shark reports as the state value
- Entity ID: `sensor.dorsalwatch_[country]_current_reports`
- Icon: shark (🦈)
- **Attributes**: 
  - `country`: Configured country
  - `state`: Configured state (if any)  
  - `reports`: Complete array of all current report data including location, shark type, time, coordinates, and all other report details

### DorsalWatch Latest Report
- Shows the timestamp of the most recent shark report
- Entity ID: `sensor.dorsalwatch_[country]_latest_report`
- Icon: shark fin
- Attributes include all fields from the latest report

### Shark Sighting Geo-Locations (Map)
- Individual geo-location entities for each shark sighting with valid coordinates
- Entity IDs: `geo_location.dorsalwatch_report_[report_id]` (e.g., `geo_location.dorsalwatch_report_47742`)
- Entity Names: Friendly names like "Bull Shark at Bondi Beach" or "Tiger Shark at Byron Bay"
- Icons: Shark icons (varies based on encounter type - tagged sharks use shark-fin icon)
- **Map Integration**: Each sighting automatically appears as a point on the Home Assistant map
- **Dynamic Management**: Entities are automatically created for new reports and removed when reports are no longer in the API response
- **Distance Calculation**: Shows distance from your home coordinates to each sighting location
- **State Value**: Distance from home in km/miles
- **Attributes**: Complete report details including:
  - All original report fields (location, shark type, time, encounter type, etc.)
  - `coordinates`: Original coordinate string from the API
  - `country`: Your configured country
  - `configured_state`: Your configured state (if any)

## Configuration

The integration fetches data every 5 minutes by default. All report data is available as sensor attributes.

**Entity Lifecycle**: Geo-location entities are dynamically managed - they are automatically created when new shark reports appear in the API and removed when reports are no longer present. This ensures your map stays current and doesn't accumulate outdated sightings.

## Usage Examples

Once installed, you'll have entities like:
- `sensor.dorsalwatch_australia_current_reports` - Shows count of current reports with all report data
- `sensor.dorsalwatch_australia_latest_report` - Shows latest report timestamp with details
- `geo_location.dorsalwatch_report_47742` - Individual shark sighting locations on the map

You can use these in:
- **Dashboards** - Display shark report counts, latest incidents, and interactive maps
- **Map** - View individual shark sighting locations with distance from home and detailed information
- **Automations** - Trigger actions when new reports are detected or when sightings occur within a certain distance from home
- **Notifications** - Alert when shark activity increases or when sightings are detected near your location

## API Information

This integration uses the public DorsalWatch API:
- **Endpoint**: `https://www.dorsalwatch.com/api/public/report/list`
- **Method**: POST
- **Authentication**: Public key based

## Troubleshooting

Check the Home Assistant logs for any error messages. The integration will log connection issues and API responses for debugging.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you find this integration helpful, please consider giving it a star ⭐

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/your_github_username/ha-dorsalwatch.svg?style=for-the-badge
[commits]: https://github.com/your_github_username/ha-dorsalwatch/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/your_github_username/ha-dorsalwatch.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/your_github_username/ha-dorsalwatch.svg?style=for-the-badge
[releases]: https://github.com/your_github_username/ha-dorsalwatch/releases