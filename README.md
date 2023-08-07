
# SensorPush (c) 2023 James Bennett

A node server for providing integration with SensorPush G1 WiFi Gateways and their associated sensors.
Uses OAuth2 for authentication with your SensorPush account and should not require any more interaction.
Still in early developement, looking for feedback!

## Installation

All that is required to run is Authenticating with your SensorPush account through the "Authenticate" tab.

### Node Settings
The settings for this node are:

#### Short Poll
   * How often to request temperature samples
#### Long Poll
   * How often to request a new access token (WARNING - Increasing this too much may lead to having to authenticate again)

#### Number of Samples
   * Number of Samples: Not used currently, but will define how many samples the rest api requests every shortPoll.


## Requirements

1. Polyglot V3.
2. ISY firmware 5.3.x or later

# Release Notes

- 0.0.1 8/7/23
   - Initial release for testing
