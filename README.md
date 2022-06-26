# BDA-Filters
Utility for determining optimal BDA filter configurations for US public safety radio channels.

<p align='center'>
<img width=100% alt='GUI screenshot' src='docs/gui.png'>
</p>

## Requirements
* Python 3.6+
* plotly

## Usage
Pass a list of channels (.csv or .txt) as an argument. If a valid solution is found, filters are output to filters.txt.

```python3 bda_filters.py "path/to/channels.csv"```

Multiple channel lists can be passed at once.

```python3 bda_filters.py "path/to/channels.csv" "path/to/moreChannels.txt"```

Channel width, filter width, and number of filters can be adjusted in [settings.py](settings.py).

## Rationale
[FCC Part 90](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-90/subpart-I/section-90.219) Class A (channelized) signal boosters have a limited number of configurable filters with variable bandwidths. Ideally, filters would be configured 1:1 with signals they are intended to amplify. This approach often fails due to delay limitations and the number and position of desired channels. Narrow filters induce long delays which can result in time delay interference or an unusable system, so filter bandwidths must be increased to reduce delays to acceptable amounts. Widening filters can cause neighboring filters to overlap, which is not possible in most BDAs. Dense groups of desired channels and/or more desired channels than available filters necessitates filters passing multiple channels.

## Solution
Channels are separated into independent subgroups in which no valid filter for one subgroup could intersect a valid filter for another. This allows each subgroup of channels to be solved independently with a blistering fast O(n!) brute force approach. A set of subsolutions, the best one per number of filters used, is returned, and the best combination of all subsolutions that fits within the maximum filters limit is selected. Solutions are scored first by number of filters used, then by the sum of the square of the ratio of channels to number of filters it passes, then by the sum of the square of the difference between channel frequency and average frequency of the filters it passes. This approach maximizes the number of filters in order to maximize control granularity for each channel, ideally targeting 1:1 filter to channel placement.

## Disclaimer
Use this tool at your own risk. None of this methodology has been reviewed or endorsed by the FCC. Ensure approval by all affected PLMRS licensees before deploying signal boosters.