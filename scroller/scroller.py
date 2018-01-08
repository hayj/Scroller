

from systemtools.basics import *
from systemtools.logger import *
from systemtools.file import *
from systemtools.location import *
from webcrawler.browser import *
import random
import time

def scroll(driver, stopFunct=None, distance=100000, sequence=100, stopAtBottom=True, scrollerParams={}):
    """
        driver param can be webcrawler.browser.Browser or a Selenium driver
        distance is the max distance
        sequence is the number of scroll to send between each stopFunct call
        stopFunct is a function which must return True if you want to stop the scrolling
        this function take the browser (or driver) in parameters
        stopAtBottom will stop the scroll if coordinates doesn't change between 2 scroll action
    """
    if isinstance(driver, Browser):
        driver = driver.driver
    scroller = iter(Scroller(**scrollerParams))
    totalDistance = 0
    previousScrollY = -1000
    # While (we don't have stop action or we have one but we don't stop yet) and we didn't walk too much:
    started = False
    while (not started or stopFunct is None or not stopFunct(driver)) and abs(totalDistance) < distance:
        started = True
        for i in range(sequence):
            # We get the scroll current data:
            newScroll = next(scroller)

            # We first sleep:
            time.sleep(newScroll["duration"])
            # And then we scroll:
            driver.execute_script("window.scrollTo(0, window.scrollY + " + str(newScroll["distance"]) + ");")
            # We check if we are on the end of page:
            if stopAtBottom:
                newScrollY = driver.execute_script("return window.scrollY")
                if previousScrollY == newScrollY:
                    return
                previousScrollY = newScrollY
            # We inc the counter:
            totalDistance += newScroll["distance"]


class Scroller:
    def __init__(self, dataDirectory=None, down=True, randomize=True, randomizeMax=0.2, filePattern="scrolldata-*.txt", logger=None, verbose=True):
        """
            By default the function will take a random scroll file
        """
        # Store all data:
        self.logger = logger
        self.verbose = verbose
        self.down = down
        self.randomize = randomize
        self.randomizeMax = randomizeMax
        # We get all lines:
        self.filePattern = filePattern
        self.dataDirectory = dataDirectory
        if self.dataDirectory is None:
            self.dataDirectory = dataDir() + "/Misc/crawling/scrolling"
        try:
            self.filePath = random.choice(sortedGlob(self.dataDirectory + "/" + self.filePattern))
        except Exception as e:
            logException(e, self, location="Scroller __init__")
            raise Exception("No scrolling data found!")

    def generateData(self):
        # We parse all lines:
        fileText = fileToStr(self.filePath)
        scrollData = []
        fileText = fileText.strip()
        fileText = fileText.split("\n")
        for current in fileText:
            current = current.split(" ")
            assert len(current[0]) > 0
            assert len(current[1]) > 0
            distance = int(current[0])
            duration = float(current[1])
            scrollData.append({"distance": distance, "duration": duration})
        # We inverse the direction:
        if not self.down:
            for current in scrollData:
                current["distance"] = -current["distance"]
        # We randomize all values:
        if self.randomize:
            for current in scrollData:
                for key in ["distance", "duration"]:
                    value = current[key]
                    variation = self.randomizeMax * abs(value)
                    variation = getRandomFloat(-variation, variation)
                    newValue = value + variation
                    current[key] = newValue
                # We re-cast the distance to int:
                current["distance"] = round(current["distance"])
            # Then we replace each 0 by a random value:
            for current in scrollData:
                if current["distance"] == 0:
                    current["distance"] = 1
                if current["duration"] == 0.0:
                    current["duration"] = getRandomFloat(0.01, 0.03)
        # We convert all duration in seconds:
        for current in scrollData:
            current["duration"] /= 1000
        return scrollData

    def __iter__(self):
        # We infinitely yield the same data profile:
        while True:
            scrollData = self.generateData()
            for current in scrollData:
                yield current

def test1():
    for current in Scroller():
        printLTS(current)
        break

def test2():
    print("START")
    b = Browser(driverType=DRIVER_TYPE.chrome, headless=False)
    b.html("file://" + execDir(__file__) + "/scroll.html")
    def stopFunct(b):
        print("stopFunct")
        if getRandomFloat() > 0.95:
            return True
        return False
    scroll(b, stopFunct=stopFunct)
    # Other examples:
#     scroll(b, distance=2000 * 100, stopAtBottom=True, stopFunct=stopFunct, scrollerParams={"dataDirectory": dataDir() + "/Misc/crawling/scrolling"})
    print("END")

if __name__ == "__main__":
    test2()




