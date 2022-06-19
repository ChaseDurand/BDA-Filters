# BDA-Filters
Utility for determining optimal BDA filter configurations for US public safety radio channels.

# Rationale
[FCC Part 90](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-90/subpart-I/section-90.219) Class A (channelized) signal boosters have a limited number of configurable filters with variable bandwidths. Ideally, filters would be configured 1:1 with signals they are intended to amplify. This approach often fails due to delay requirements and the number and position of desired channels. Narrow filters induce long delays which can result in time delay interference or an unusable system, so filter bandwidths must be increase to reduce delays to acceptable amounts. Widening filters can cause neighboring filters to overlap, which is not possible in most BDAs. Dense groups of desired channels and/or more desired channels than available filters necessitates filters passing multiple channels.

# Usage
Pass a list of channels (.csv or .txt) as an argument:

```python3 bda_filters.py "path/to/channels.csv"```

Multiple channel lists can be passed at once:

```python3 bda_filters.py "path/to/channels.csv" "path/to/moreChannels.txt"```

# Requirements
* python 3.10+
* plotly


# Disclaimer
Use this tool at your own risk. None of this methodology has been reviewed or endorsed by the FCC or any AHJ.