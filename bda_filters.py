import sys
import plotly.graph_objects as go
import itertools
import copy
from settings import filterWidth, channelWidth, filterCountMax
from gui import drawSplit, drawUncoveredChannel, drawConflict, renderGUI

class Channel:
    def __init__(self, freqCenter, width=12500):
        self.freqCenter = freqCenter
        self.freqLow = freqCenter - int(width/2)
        self.freqHigh = freqCenter + int(width/2)
    def __lt__(self, other):
        return self.freqCenter < other.freqCenter
    def __str__(self):
        return str(self.freqCenter)

class Filter:
    def __init__(self, freqCenter, width=75000):
        self.freqCenter = freqCenter
        self.freqLow = freqCenter - int(width/2)
        self.freqHigh = freqCenter + int(width/2)
        self.width = width
        self.channels = []
        self.channelScore = 0
        self.centerScore = 0
    def __str__(self):
        return str(self.freqCenter)
    def calcFilterChannelScore(self):
        self.channelScore = -1 * (len(self.channels) * len(self.channels))
        return
    def calcFilterCenterScore(self):
        freqSum = 0
        for channel in self.channels:
            freqSum += channel.freqCenter
        freqAverage = int(freqSum / len(self.channels))
        delta = (self.freqCenter - freqAverage) / 1000000
        self.centerScore = -1 * (delta * delta)
        return

class SubSolution:
    def __init__(self, filters, channels):
        self.filters = filters
        self.filterCount = len(filters)
        self.channels = channels
        self.channelScore = sum(f.channelScore for f in filters) / self.filterCount
        self.centerScore = sum(f.centerScore for f in filters) / self.filterCount

class Solution:
    def __init__(self, subSolutions):
        self.subSolutions = subSolutions
        self.filterCount = sum(s.filterCount for s in subSolutions)
        self.channelScore = sum(s.channelScore for s in subSolutions) / len(subSolutions)
        self.centerScore = sum(s.centerScore for s in subSolutions) / len(subSolutions)

# Given channels and a filter, return all filters passed by the channel
def getChannelsInFilter(filter, channels):
    channelsInFilter = []
    for channel in channels:
        if(checkChannelInFilter(filter, channel)):
            channelsInFilter.append(channel)
    return channelsInFilter

channelWidthHalf = int(channelWidth/2)
filterWidthHalf = int(filterWidth/2)
searchGranularity = int(channelWidthHalf/1) #TODO find minimum value


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
    return (filter.freqLow <= channel.freqLow <= filter.freqHigh)\
        and (filter.freqLow <= channel.freqHigh <= filter.freqHigh)

# Given a filter and channel, check if the filter edge falls within the channel
def checkFilterSplit(filter, channel):
    return not ((channel.freqLow < filter.freqLow < channel.freqHigh)\
        or (channel.freqLow < filter.freqHigh < channel.freqHigh))

# Given two filters of identical width, check if filters overlap.
# If filters overlap (invalid), return True.
# If filters don't overlap, return False. 
def checkFilterOverlap(filter1, filter2):
    return (filter1.freqLow < filter2.freqHigh) and (filter2.freqLow < filter1.freqHigh)

# Check if channel is fully passed by only one filter in filter list
def checkChannel(fig, channel, filters):
    filterCount = 0
    for filter in filters:
        if (filter.freqLow <= channel.freqLow <= filter.freqHigh) and (filter.freqLow <= channel.freqHigh <= filter.freqHigh):
            filterCount += 1
    if filterCount == 0:
        print("Channel", channel.freqCenter, "not passed!")
        drawUncoveredChannel(fig, channel)
    elif filterCount > 1:
        print("Channel", channel.freqCenter, "covered by multiple filters!")
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
def channelsAreIndependent(channel1, channel2):
    return (channel2.freqCenter-channel1.freqCenter) + channelWidth >= 2 * filterWidth

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
                drawSplit(fig, 0.5*(channels[i].freqCenter+channels[i-1].freqCenter))
                lowIndex = i       
    return channelRanges



def solveChannelsRec(subChannels, solutions, channelsCopy, newFilters):
    # If no channels remain to be covered, we're done.
    if len(channelsCopy) == 0:
        solution = SubSolution(newFilters, subChannels)
        # Reduce solutions to best solution per number of filters
        if solution.filterCount in solutions:
            # If we already have a solution for this number of filters, only save best.
            solutionOptions = [solution, solutions[solution.filterCount]]
            solutionOptions.sort(key=lambda i: (i.filterCount, i.channelScore, i.centerScore))
            solutions[solution.filterCount] = solutionOptions[-1]
        else:
            solutions[solution.filterCount] = solution
        return
    # Find min and max
    fLow = min(channelsCopy).freqCenter + channelWidthHalf - filterWidthHalf
    fHigh = (max(channelsCopy).freqCenter - channelWidthHalf) + filterWidthHalf
    for grid in range(fLow, fHigh + channelWidthHalf, searchGranularity):
        newFiltersCopy = copy.copy(newFilters)
        channelsCopyRec = copy.copy(channelsCopy)
        newFilter = Filter(grid)
        if(validateFilter(newFilter, newFiltersCopy, channelsCopy)):
            channelsInFilter = getChannelsInFilter(newFilter, channelsCopyRec)
            newFilter.channels = channelsInFilter
            newFilter.calcFilterCenterScore()
            newFilter.calcFilterChannelScore()
            # Add filter to existing filter list
            newFiltersCopy.append(newFilter)
            # Remove channels covered by new filter to create new channel subsets
            for channel in channelsInFilter:
                channelsCopyRec.remove(channel)
            # solve recurrsively
            solveChannelsRec(channelsCopy, solutions, channelsCopyRec, newFiltersCopy)
    return

def solveChannels(channels):
    # Pick filter
    # if valid, solve recurrisvely
    fLow = min(channels).freqCenter + channelWidthHalf - filterWidthHalf
    fHigh = (max(channels).freqCenter - channelWidthHalf) + filterWidthHalf
    solutions = {}
    for grid in range(fLow, fHigh + searchGranularity, searchGranularity):
        channelsCopy = copy.copy(channels)
        newFilters = []
        # Pick filter
        newFilter = Filter(grid)
        if(validateFilter(newFilter, newFilters, channelsCopy)):
            channelsInFilter = getChannelsInFilter(newFilter, channelsCopy)
            newFilter.channels = channelsInFilter
            newFilter.calcFilterCenterScore()
            newFilter.calcFilterChannelScore()
            # Add filter to existing filter list
            newFilters.append(newFilter)
            # Remove channels covered by new filter to create new channel subsets
            for channel in channelsInFilter:
                channelsCopy.remove(channel)
            # solve recurrsively
            solveChannelsRec(channels, solutions, channelsCopy, newFilters)
    return solutions

def getChannelsFromFile(filePath, channelsAll):
    f = open(filePath,"r")
    for line in f.read().splitlines():
        freq = float(line.replace(",",""))
        # If input is in MHz, convert to Hz.
        if freq < 1000:
            freq = freq * 1000000
        # Check if input is within US Dl ranges.
        if not((758000000 <= freq <= 775000000) or (851000000 <= freq <= 869000000)):
            print("Error:", freq, "is outside of US DL ranges.")
            exit(1)

        freq = int(freq)
        # Check for duplicate channels
        if any(channel.freqCenter == freq for channel in channelsAll):
            print("Error:", freq, "appears in input twice.")
            exit(1)
        # Add channel to list
        channelsAll.append(Channel(freq))
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
    subgroupSolutions = [None] * len(channelSubgroups)
    for i in range(0, len(channelSubgroups)):
        channelSubgroup = channelSubgroups[i]
        print("Solving subset of size", len(channelSubgroup))
        if len(channelSubgroup) == 1:
            # Add filters 1:1 to single isolated channels
            newFilter = Filter(channelSubgroup[0].freqCenter)
            newFilter.channels = [channelSubgroup[0]]
            newFilter.calcFilterChannelScore()
            newFilter.calcFilterCenterScore()
            subgroupSolutions[i] = {1: SubSolution([newFilter], channelSubgroup)}
        else:
            subgroupSolutions[i] = solveChannels(channelSubgroup)

    solutionCombos = list(itertools.product(*subgroupSolutions))

    solutions = []

    for s in solutionCombos:
        subSolutionList = []
        for i in range(0, len(s)):
            subSolutionList.append(subgroupSolutions[i][s[i]])
        solutions.append(Solution(subSolutionList))

    solutions.sort(key=lambda i: (i.filterCount, i.channelScore, i.centerScore))
    
    print("Max filter solution uses", solutions[-1].filterCount, "filters.")
    print("Min filter solution uses", solutions[0].filterCount, "filters.")

    # Traverse solution list until filter count is within limit.
    filters = []
    for i in reversed(range(0, len(solutions))):
        if solutions[i].filterCount <= filterCountMax:
            # Solution within limits has been found.
            # Print results and write to file.
            # Render GUI.
            print("Best solution within limits:", solutions[i].filterCount, solutions[i].channelScore, solutions[i].centerScore)
            for s in solutions[i].subSolutions:
                filters += s.filters
            checkSolution(fig, channelsAll, filters)
            print("Filters used:",len(filters))
            f = open("filters.txt", "w")
            for filter in filters:
                print(filter)
                f.write(str(filter)+",\n")
            f.close()
            renderGUI(fig, channelsAll, filters)
            exit(0)
    print("Error: No solution for", filterCountMax, "filters.")
    exit(0)

if __name__ == "__main__":
    main()