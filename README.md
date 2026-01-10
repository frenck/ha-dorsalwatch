# DorsalWatch Home Assistant Integration

A custom Home Assistant integration for monitoring shark reports from the DorsalWatch API.

## Installation

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

The integration provides two sensors:

### DorsalWatch Report Count
- Shows the total number of shark reports
- Entity ID: `sensor.dorsalwatch_[country]_report_count`
- Icon: shark (🦈)

### DorsalWatch Latest Report
- Shows details of the most recent shark report
- Entity ID: `sensor.dorsalwatch_[country]_latest_report`
- Icon: shark fin
- Attributes include all fields from the latest report

## Configuration

The integration fetches data every 5 minutes by default. All report data is available as sensor attributes.

## API Information

This integration uses the public DorsalWatch API:
- **Endpoint**: `https://www.dorsalwatch.com/api/public/report/list`
- **Method**: POST
- **Authentication**: Public key based

## Troubleshooting

Check the Home Assistant logs for any error messages. The integration will log connection issues and API responses for debugging.