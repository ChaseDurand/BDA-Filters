from settings import *

def drawSplit(fig, freqCenter):
    freqLow = freqCenter - 0.2 * channelWidth
    freqHigh = freqCenter + 0.2 * channelWidth

    fig.add_shape(type="rect",
        x0=freqLow, y0=0, x1=freqHigh, y1=1,
        line=dict(
            color="rgba(150,200,100,0.8)",
            width=2,
        ),
        fillcolor="rgba(150,200,100,0.6)",
    ) 

def drawChannel(fig, freqCenter):
    freqLow = freqCenter - 0.5 * channelWidth
    freqHigh = freqCenter + 0.5 * channelWidth

    fig.add_shape(type="rect",
        x0=freqLow, y0=0, x1=freqHigh, y1=0.5,
        line=dict(
            color="rgba(25,41,88,0.8)",
            width=2,
        ),
        fillcolor="rgba(135,206,250,0.6)",
    )

def drawUncoveredChannel(fig, freqCenter):
    freqLow = freqCenter - 0.5 * channelWidth
    freqHigh = freqCenter + 0.5 * channelWidth

    fig.add_shape(type="rect",
        x0=freqLow, y0=0.51, x1=freqHigh, y1=0.54,
        line=dict(
            color="rgba(25,41,88,0.8)",
            width=2,
        ),
        fillcolor="rgba(135,206,250,0.6)",
    )

def drawFilter(fig, freqCenter):
    freqLow = freqCenter - 0.5 * filterWidth
    freqHigh = freqCenter + 0.5 * filterWidth

    fig.add_shape(type="rect",
        x0=freqLow, y0=0.55, x1=freqHigh, y1=0.75,
        line=dict(
            color="rgba(70,13,13,0.8)",
            width=2,
        ),
        fillcolor="rgba(200,50,31,0.6)",
    )

def drawConflict(fig, freqCenter):
    freqLow = freqCenter - 0.5 * filterWidth
    freqHigh = freqCenter + 0.5 * filterWidth

    fig.add_shape(type="rect",
        x0=freqLow, y0=0.80, x1=freqHigh, y1=0.95,
        line=dict(
            color="rgba(70,13,13,0.8)",
            width=2,
        ),
        fillcolor="rgba(200,50,31,0.6)",
    )