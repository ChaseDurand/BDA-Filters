import plotly.graph_objects as go
import itertools
import copy
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
        # if checkFilterOverlap(newFilter, filter):
        #     print("filters can't overlap!")

    # Filter must contain a channel
    filterContainsChannel = False
    for channel in channels:
        filterContainsChannel = filterContainsChannel or checkChannelInFilter(newFilter, channel)

    filterValid = filterValid and filterContainsChannel
    return filterValid

# Given a filter and channel, check if channel is within filter
def checkChannelInFilter(filter, channel):
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
    # if (x1 < y2) and (y1 < x2):
    #     print(x1, x2, y1, y2)
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

# Given channels and a filter, return all filters passed by the channel
def getChannelsInFilter(channels, filter):
    channelList = []
    for channel in channels:
        if checkChannelInFilter(filter, channel):
            channelList.append(channel)
    return channelList

def solveChannelsRec(solutions, channels, existingFilters, newFilters):
    # print("called rec with channels", channels)
    # If no channels remain to be covered, we're done.
    if len(channels) == 0:
        solutions.append(newFilters)
        return
    # Find min and max
    fLow = min(channels) + channelWidthHalf - filterWidthHalf
    fHigh = max(channels) - channelWidthHalf + filterWidthHalf
    for grid in range(fLow, fHigh + channelWidthHalf, channelWidthHalf):
        channelsCopyRec = copy.deepcopy(channels)
        newFilter = grid
        if(validateFilter(newFilter, existingFilters+newFilters, channels)):
            # Add filter to existing filter list
            newFilters.append(newFilter)
            # print("Adding filter:", newFilter)
            # Remove channels covered by new filter to create new channel subsets
            channelsInFilter = getChannelsInFilter(channelsCopyRec, newFilter)
            for channel in channelsInFilter:
                channelsCopyRec.remove(channel)
            # solve recurrsively
            solveChannelsRec(solutions, channelsCopyRec, existingFilters, newFilters)
    return

def solveChannels(fig, channels, existingFilters):
    # print("existing filters", existingFilters)
    print("called solve with channels", channels)
    # Pick filter
    # if valid, solve recurrisvely
    # Minimum low filter center = channel + 1/2 channelWidth - 1/2 filterWidth
    # Maximum high filter center = channel - 1/2 channelWidth + 1/2 filterWidth
    fLow = min(channels) + channelWidthHalf - filterWidthHalf
    fHigh = max(channels) - channelWidthHalf + filterWidthHalf
    solutions = []
    for grid in range(fLow, fHigh + searchGranularity, searchGranularity):
        # print("Starting with grid", grid, "and channels", channels)
        channelsCopy = copy.deepcopy(channels)
        newFilters = []
        # Pick filter
        newFilter = grid
        if(validateFilter(newFilter, existingFilters+newFilters, channelsCopy)):
            # print("validated filter", newFilter)
            # Add filter to existing filter list
            newFilters.append(newFilter)
            # print("Adding filter:", newFilter)
            # Remove channels covered by new filter to create new channel subsets
            channelsInFilter = getChannelsInFilter(channelsCopy, newFilter)
            for channel in channelsInFilter:
                channelsCopy.remove(channel)
            # solve recurrsively
            solveChannelsRec(solutions, channelsCopy, existingFilters, newFilters)
            # print("filter solutions:",solutions)
        # else:
            # print("filter invalid", newFilter)
        # exit()
    # exit()
    # drawFilter(fig, fLow+searchGranularity)
    # drawFilter(fig, fHigh)
    # print(len(solutions))
    # for solution in solutions:
    #     print(len(solution))
    # exit()
    return solutions

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
        else:
            solutions = solveChannels(fig, channelSubset, filters)
            filters = filters+max(solutions, key=len)


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
    print("filters used:",len(filters))
    exit()

if __name__ == "__main__":
    main()