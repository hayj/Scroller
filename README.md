
# Scroller

This tools can simulate human scrolling using recorded scroll and randomize mechanism.

## Install

You must install all dependencies in `wm-dist` and specify the data directory when you use the class or function

    pip install ./wm-dist/*.gz

So you just need to download the `wm-dist` dir and the `data` dir to use this tool.

Then you can import it using:

    from scroller.scroller import *

## Function `scroll()`

Usage:

    scroll(seleniumDriver, distance=1000)

This function use the class Scroller, you can use Scroller class args in the scroll function:

    scroll(driver, stopFunct=myStopFunct, dataDirectory="/MY_DATA_DIR", fast=True)

## Class `Scroller`

This class generate human scroll data. See parameters for more informations.

    for current in Scroller():
        print(current)