import plotly.graph_objects as go
import itertools
from settings import *
from gui import *

def validateFilter(newFilter, filters, channels):
    filterValid = True
    # Filter can't split channel
    for channel in channels:    
        filterValid = filterValid and checkFilterSplit(newFilter, channel)

    # Filter can't overlap other filter
    for filter in filters:
        filterValid = filterValid and not checkFilterOverlap(newFilter, filter)
        if checkFilterOverlap(newFilter, filter):
            print("filters can't overlap!")

    # Filter must contain a channel
    filterContainsChannel = False
    for channel in channels:
        filterContainsChannel = filterContainsChannel or checkFilterInChannel(newFilter, channel)

    filterValid = filterValid and filterContainsChannel
    return filterValid

# Given a filter and channel, check if filter is within channel
def checkFilterInChannel(filter, channel):
    cLower = channel - channelWidthHalf
    cUpper = channel + channelWidthHalf
    fLower = filter - filterWidthHalf
    fUpper = filter + filterWidthHalf
    return (fLower <= cLower <= fUpper) and (fLower <= cUpper <= fUpper)

# Given a filter and channel, check if the filter edge falls within the channel
def checkFilterSplit(filter, channel):
    fLower = filter - filterWidthHalf
    fUpper = filter + filterWidthHalf
    cUpper = channel + channelWidthHalf
    cLower = channel - channelWidthHalf
    return not ((cLower < fLower < cUpper) or (cLower < fUpper < cUpper))

# Check if filters overlap
def checkFilterOverlap(freq1, freq2):
    x1 = freq1 - filterWidthHalf
    x2 = freq1 + filterWidthHalf
    y1 = freq2 - filterWidthHalf
    y2 = freq2 + filterWidthHalf
    if (x1 < y2) and (y1 < x2):
        print(x1, x2, y1, y2)
    return (x1 < y2) and (y1 < x2)

# Check if channel is fully passed by only one filter in filter list
def checkChannel(fig, channel, filters):
    channel1 = channel - channelWidthHalf
    channel2 = channel + channelWidthHalf
    filterCount = 0
    for filter in filters:
        filter1 = filter - filterWidthHalf
        filter2 = filter + filterWidthHalf
        if (filter1 <= channel1 <= filter2) and (filter1 <= channel2 <= filter2):
            filterCount += 1
    if filterCount == 0:
        print("Channel", channel, "not passed!")
        drawUncoveredChannel(fig, channel)
    elif filterCount > 1:
        print("Channel", channel, "covered by multiple filters!")
        drawUncoveredChannel(fig, channel)
    return filterCount == 1

def checkSolution(fig, channels, filters):
    validSolution = True
    filterCombos = list(itertools.combinations(filters, 2))

    for filterPair in filterCombos:
        if checkFilterOverlap(filterPair[0], filterPair[1]):
            # Channels overlap
            validSolution = False
            print("Filter overlap between ", filterPair[0], filterPair[1])
            drawConflict(fig, filterPair[0])
            drawConflict(fig, filterPair[1])

    for channel in channels:
        if checkChannel(fig, channel, filters) == False:
            validSolution = False

    print("Valid solution:", validSolution)
    return validSolution

def channelsAreIndependent(f1, f2):
    return (f2-f1) + channelWidth >= 2 * filterWidth

def splitChannels(fig, channels):
    channels.sort()
    channelRanges = []

    lowIndex = 0
    for i in range(0, len(channels)+1):
        if i == len(channels):
            channelRanges.append(channels[lowIndex:i])
        elif i != lowIndex:
            if channelsAreIndependent(channels[i-1], channels[i]):
                channelRanges.append(channels[lowIndex:i])
                drawSplit(fig, 0.5*(channels[i]+channels[i-1]))
                lowIndex = i       
    return channelRanges

def main():
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[1.5, 4.5],
        y=[0.75, 0.75],
        text=["Unfilled Rectangle", "Filled Rectangle"],
        mode="text",
    ))

    channels = [854337500,
                854612500,
                855987500,
                856487500,
                856662500,
                856987500,
                857487500,
                857987500,
                858487500,
                858987500,
                859487500,
                859987500,
                851037500,
                851150000,
                851200000,
                851262500,
                851287500,
                851462500,
                851537500,
                851625000,
                851650000,
                851762500,
                851962500,
                852150000,
                852262500,
                852650000,
                852787500,
                852962500,
                853150000,
                853200000,
                853262500,
                853462500,
                853650000,
                853762500,
                853925000,
                853962500,
                855462500]

    channelsReduced = splitChannels(fig, channels)

    # filterCountUnused = filterCountMax - (len(channels) - len(channelsReduced))
    # print(filterCountUnused)

    filters = []

    # Add filters 1:1 to single isolated channels
    for channelSubset in channelsReduced:
        if len(channelSubset) == 1:
            filters.append(channelSubset[0])

    # for channelSubset in channelsReduced:
    #     if len(channelSubset) != 1:

    #         print(channelSubset[0], validateFilter(channelSubset[0],filters, channelSubset))
    #         filters.append(channelSubset[0])

    plotFreqMargin = 200000 # Padding to add to sides of plot
    freqRange = [min(min(channels), min(filters)) - plotFreqMargin, max(max(channels), max(filters)) + plotFreqMargin]

    # Set axes properties
    fig.update_xaxes(range=freqRange, showgrid=False)
    fig.update_yaxes(range=[0, 1])
    
    for channel in channels:
        drawChannel(fig, channel)

    for filter in filters:
        drawFilter(fig, filter)

    checkSolution(fig, channels, filters)

    fig.update_shapes(dict(xref='x', yref='y'))
    fig.show()
    exit()

if __name__ == "__main__":
    main()