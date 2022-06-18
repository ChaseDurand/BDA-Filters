import sys
import plotly.graph_objects as go
import itertools
import copy
from settings import *
from gui import *
from testData.testChannels import *

class Channel:
    def __init__(self, freqCenter, width=12500):
        self.freqCenter = freqCenter
        self.freqLow = freqCenter - int(width/2)
        self.freqHigh = freqCenter + int(width/2)


class Filter:
    def __init__(self, freqCenter, width=75000):
        self.freqCenter = freqCenter
        self.freqLow = freqCenter - int(width/2)
        self.freqHigh = freqCenter + int(width/2)
        self.width = width
        self.channels = []

class Solution:
    def __init__(self, filters, channels):
        self.filters = filters
        self.filterCount = len(filters)
        self.channels = channels



channelWidthHalf = int(channelWidth/2)
filterWidthHalf = int(filterWidth/2)
searchGranularity = int(channelWidthHalf/2) #TODO find minimum value

# Given a potential filter, existing filters, and channels, check if new filter is valid.
# If filter is valid, return True.
# If not valid, return False.
def validateFilter(newFilter, filters, channels):
    filterValid = True
    # Filter can't split a channel. Channel must be fully in or out of filter.
    for channel in channels:    
        filterValid = filterValid and checkFilterSplit(newFilter, channel)

    # Filter can't overlap any other filter.
    for filter in filters:
        filterValid = filterValid and not checkFilterOverlap(newFilter, filter)

    # Filter must fully pass at least one channel.
    filterContainsChannel = False
    for channel in channels:
        filterContainsChannel = filterContainsChannel or checkChannelInFilter(newFilter, channel)

    filterValid = filterValid and filterContainsChannel
    return filterValid

# Given a filter and channel, check if channel is within filter
# Given a filter and channel, check if the channel is fully passed by filter.
# If channel fully passes, return True.
# If not, return False.
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

# Given two filters of identical width, check if filters overlap.
# If filters overlap (invalid), return True.
# If filters don't overlap, return False. 
def checkFilterOverlap(filter1, filter2):
    f1Lower = filter1 - filterWidthHalf
    f1Upper = filter1 + filterWidthHalf
    f2Lower = filter2 - filterWidthHalf
    f2Upper = filter2 + filterWidthHalf
    return (f1Lower < f2Upper) and (f2Lower < f1Upper)

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

# Check if set of channels and filters are valid.
# Solution is valid if no filters overlap and if all channels are fully passed.
# Return True if valid.
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

# Check if channels are far enough apart such that no valid filter on one could affect the other.
# If indpendent, return True.
# If not, return False.
def channelsAreIndependent(f1, f2):
    return (f2-f1) + channelWidth >= 2 * filterWidth

# Given a list of channels, split channels into independent groups.
# Return list of list of channels.
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
            # Remove channels covered by new filter to create new channel subsets
            channelsInFilter = getChannelsInFilter(channelsCopyRec, newFilter)
            for channel in channelsInFilter:
                channelsCopyRec.remove(channel)
            # solve recurrsively
            solveChannelsRec(solutions, channelsCopyRec, existingFilters, newFilters)
    return

def solveChannels(channels, existingFilters):
    # Pick filter
    # if valid, solve recurrisvely
    fLow = min(channels) + channelWidthHalf - filterWidthHalf
    fHigh = max(channels) - channelWidthHalf + filterWidthHalf
    solutions = []
    for grid in range(fLow, fHigh + searchGranularity, searchGranularity):
        channelsCopy = copy.deepcopy(channels)
        newFilters = []
        # Pick filter
        newFilter = grid
        if(validateFilter(newFilter, existingFilters+newFilters, channelsCopy)):
            # Add filter to existing filter list
            newFilters.append(newFilter)
            # Remove channels covered by new filter to create new channel subsets
            channelsInFilter = getChannelsInFilter(channelsCopy, newFilter)
            for channel in channelsInFilter:
                channelsCopy.remove(channel)
            # solve recurrsively
            solveChannelsRec(solutions, channelsCopy, existingFilters, newFilters)
    return solutions

def getChannelsFromFile(filePath, channelsAll):
    f = open(filePath,"r")
    for line in f.read().splitlines():
        channel = float(line.replace(",",""))
        # If input is in MHz, convert to Hz.
        if channel < 1000:
            channel = channel * 1000000
        # Check if input is within US Dl ranges.
        if not((758000000 <= channel <= 775000000) or (851000000 <= channel <= 869000000)):
            print("Error:", channel, "is outside of US DL ranges.")
            exit(1)

        channel = int(channel)
        # Check for duplicate channels
        if channel in channelsAll:
            print("Error:", channel, "appears in input twice.")
            exit(1)
        # Add channel to list
        channelsAll.append(channel)
    return

def main():
    if(len(sys.argv)==1):
        print("Error: Please provide path to channel lists (csv/txt) as argument.")
        exit(1)
    
    # Get channels from file arguments
    channelsAll = []
    for path in sys.argv[1:]:
        getChannelsFromFile(path, channelsAll)

    print("Channels:", len(channelsAll))

    fig = go.Figure()

    # Split channels into independent subgroups
    # Solve all subgroups
    # Find best solution

    channelSubgroups = splitChannels(fig, channelsAll)

    # filterCountUnused = filterCountMax - (len(channels) - len(channelsReduced))
    # print(filterCountUnused)

    filters = []

    # Add filters 1:1 to single isolated channels
    for channelSubgroup in channelSubgroups:
        if len(channelSubgroup) == 1:
            filters.append(channelSubgroup[0])
        else:
            solutions = solveChannels(channelSubgroup, filters)
            filters = filters+max(solutions, key=len)

    plotFreqMargin = 200000 # Padding to add to sides of plot
    freqRange = [min(min(channelsAll), min(filters)) - plotFreqMargin, max(max(channelsAll), max(filters)) + plotFreqMargin]

    # Set axes properties
    fig.update_xaxes(range=freqRange, showgrid=False)
    fig.update_yaxes(range=[0, 1])
    
    for channel in channelsAll:
        drawChannel(fig, channel)

    for filter in filters:
        drawFilter(fig, filter)

    checkSolution(fig, channelsAll, filters)

    fig.update_shapes(dict(xref='x', yref='y'))
    fig.show()
    print("filters used:",len(filters))
    
    print(filters)
    exit()

if __name__ == "__main__":
    main()