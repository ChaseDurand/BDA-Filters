from settings import filterWidth, channelWidth, plotFreqMargin

# Draw a line separating independent channel groups.
def drawSplit(fig, freq):
    fig.add_shape(type="rect",
        x0=freq, y0=0, x1=freq, y1=1,
        line=dict(
            color="rgba(150,150,150,0.8)",
            width=3,
            dash="dash",
        ),
        fillcolor="rgba(150,150,150,0.6)",
    ) 

# Draw a channel.
def drawChannel(fig, channel):
    fig.add_shape(type="rect",
        x0=channel.freqLow, y0=0, x1=channel.freqHigh, y1=0.5,
        line=dict(
            color="rgba(20,100,50,0.8)",
            width=2,
        ),
        fillcolor="rgba(150,200,100,0.6)",
    )

# Draw an indicator for a channel that is not passed.
def drawUncoveredChannel(fig, channel):
    fig.add_shape(type="rect",
        x0=channel.freqLow, y0=0.51, x1=channel.freqHigh, y1=0.54,
        line=dict(
            color="rgba(25,41,88,0.8)",
            width=2,
        ),
        fillcolor="rgba(135,206,250,0.6)",
    )

# Draw filter.
def drawFilter(fig, filter):
    fig.add_shape(type="rect",
        x0=filter.freqLow, y0=0.55, x1=filter.freqHigh, y1=0.75,
        line=dict(
            color="rgba(25,41,88,0.8)",
            width=2,
        ),
        fillcolor="rgba(135,206,250,0.6)",
    )

# Draw an indicator for a filter that overlaps with another filter.
def drawConflict(fig, filter):
    fig.add_shape(type="rect",
        x0=filter.freqLow, y0=0.80, x1=filter.freqHigh, y1=0.95,
        line=dict(
            color="rgba(70,13,13,0.8)",
            width=2,
        ),
        fillcolor="rgba(200,50,31,0.6)",
    )

def renderGUI(fig, channels, filters):
    freqRange = [min(min(channels, key=lambda channel: channel.freqCenter).freqCenter,\
        min(filters, key=lambda filter: filter.freqCenter).freqCenter) - plotFreqMargin,\
            max(max(channels, key=lambda channel: channel.freqCenter).freqCenter,\
                max(filters, key=lambda filter: filter.freqCenter).freqCenter) + plotFreqMargin]
    # Set axes properties
    fig.update_xaxes(range=freqRange, showgrid=False)
    fig.update_yaxes(range=[0, 1])
    
    for channel in channels:
        drawChannel(fig, channel)

    for filter in filters:
        drawFilter(fig, filter)

    fig.update_shapes(dict(xref='x', yref='y'))
    fig.show()
    return