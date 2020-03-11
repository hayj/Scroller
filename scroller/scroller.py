

from systemtools.basics import *
from systemtools.logger import *
from systemtools.file import *
from systemtools.location import *
from selenium import webdriver
try:
    from hjwebbrowser.browser import *
except: pass
import random
import time
try:
    from datastructuretools.setqueue import *
except: pass

def getPageInfos(driver):
    getDocHeightFunction = "function getDocHeightForPythonScroller() { var D = document; return Math.max(D.body.scrollHeight, D.documentElement.scrollHeight, D.body.offsetHeight, D.documentElement.offsetHeight, D.body.clientHeight, D.documentElement.clientHeight); };"
    documentHeight = driver.execute_script(getDocHeightFunction + " " + "return getDocHeightForPythonScroller();")
    windowHeight = driver.execute_script("return window.innerHeight;")
    scrollTop = driver.execute_script("return window.scrollY;")
    scrollBottom = scrollTop + windowHeight
    result = (scrollTop, scrollBottom, windowHeight, documentHeight)
    return result

def executeScroll(driver, distance):
    driver.execute_script("window.scrollTo(0, window.scrollY + " + str(distance) + ");")

def moveTo(driver, element):
    action = webdriver.ActionChains(driver)
    action.move_to_element(element)
    action.perform()

def scrollTo(driver, element, *args, **kwargs):
    """
        This function use continuousScroll to scroll to an element
        The page is centered to the element
        You can give smartScroll parameters in *args, **kwargs
    """
    y = element.location["y"]
    (scrollTop, scrollBottom, windowHeight, documentHeight) = getPageInfos(driver)
    scrollMiddle = int(scrollTop + windowHeight / 2)
    scrollMiddleTop = int(scrollMiddle - windowHeight / 16)
    scrollMiddleBottom = int(scrollMiddle + windowHeight / 16)
    randomScrollMiddle = getRandomInt(scrollMiddleTop, scrollMiddleBottom)
    yShift = randomScrollMiddle - scrollTop
    distance = abs(randomScrollMiddle - y)
    down = True
    if randomScrollMiddle > y:
        down = False
    smartScroll \
    (
        driver,
        stopFunct=None,
        distance=distance,
        sequence=6,
        stopAtBorder=True,
        down=down,
        reverseScrollProb=0.0,
        *args, **kwargs
    )
    driver.execute_script("window.scrollTo(0, " + str(y - yShift) + ");")

def scrollContinueCondition\
(
    started,
    stopFunct,
    driver,
    totalDistance,
    minScrollTopReached,
    maxScrollBottomReached,
    distance,
    **kwargs,
):
    return \
    (
        (
            not started
            or stopFunct is None
            or not stopFunct(driver,
                             totalDistance=totalDistance,
                             minScrollTopReached=minScrollTopReached,
                             maxScrollBottomReached=maxScrollBottomReached,
                             **kwargs,)
        )
        and (distance is None or abs(totalDistance) < abs(distance))
    )

def smartScroll \
(
    driver,
    stopFunct=None,
    stopFunctKwargs={},
    distance=None,
    sequence=100,
    stopAtBorder=False,
    distancePerSecond=10000, # 10000
    sleepMin=0.0001,
    sleepMax=0.002,
    randomGapRatio=0.2,
    logger=None,
    verbose=True,
    down=True,
    timeout=3600,
    reverseScrollProb=0.5,
    reverseScrollDistance=None,
    reverseScrollEachTraveledDistance=5000,
    humanBreaks=False,
    humanBreaksMinDuration=0.15,
    stopWhenDocHeightNotChangedSince=None, # seconds
):
    """
        See the README
    """
    if distance is not None and distance < 0:
        logError("SCROLL CRITICAL ERROR: distance must be greater or equals to 0!",
                 logger=logger, verbose=verbose)
        return
    if distance is not None and distance == 0:
        return
    try:
        if isinstance(driver, Browser):
            driver = driver.driver
    except: pass
    # Here we init some vars:
    startTime = time.time()
    (scrollTop, scrollBottom, windowHeight, documentHeight) = getPageInfos(driver)
    minScrollTopReached = scrollTop
    maxScrollBottomReached = scrollBottom
    previousDocumentHeight = documentHeight
    previousDocumentHeightTimestamp = time.time()
    totalDistance = 0
    started = False
    traveledDistanceSincePreviousReverseScroll = 0
    # We set default reverseScrollDistance:
    if reverseScrollDistance is None:
        reverseScrollDistance = int(windowHeight + 0.2 * windowHeight)
    # And while we can continue:
    while scrollContinueCondition \
    (
        started,
        stopFunct,
        driver,
        totalDistance,
        minScrollTopReached,
        maxScrollBottomReached,
        distance,
        **stopFunctKwargs,
    ):
        # We can sleep if we introduce breaks:
        if humanBreaks:
            randomSleep(humanBreaksMinDuration, 6 * humanBreaksMinDuration)
        # We start and get the previousTimestamp which is the first of the sequence:
        started = True
        previousTimestamp = None
        previousScrollTop = scrollTop
        for i in range(sequence):
            # For the first iteration we sleep:
            if previousTimestamp is None:
                previousTimestamp = time.time()
                randomSleep(sleepMin, sleepMax)
            # First we calculate the distance to walk:
            timeSpent = time.time() - previousTimestamp
            if timeSpent < 0:
                timeSpent = 0.0
            previousTimestamp = time.time()
            expectedDistance = distancePerSecond * timeSpent
            expectedDistanceMin = int(expectedDistance - randomGapRatio * expectedDistance)
            if expectedDistanceMin == 0:
                expectedDistanceMin = 1
            expectedDistanceMax = int(expectedDistance + randomGapRatio * expectedDistance)
            if expectedDistanceMax == 0:
                expectedDistanceMax = 1
            expectedDistance = getRandomInt(expectedDistanceMin, expectedDistanceMax)
            # We check the expectedDistance:
            if expectedDistance <= 0:
                logError("SCROLL CRITICAL ERROR: expectedDistance = " + str(expectedDistance),
                         logger=logger, verbose=verbose)
                return
            # We reduce expectedDistance if it's too much:
            if distance is not None:
                remainingDistance = distance - totalDistance
                if remainingDistance == 0:
                    return
                elif remainingDistance < 0:
                    logError("SCROLL CRITICAL ERROR: the remaining distance is < 0 !!!",
                            logger=logger, verbose=verbose)
                    return
                elif remainingDistance < expectedDistance:
                    expectedDistance = remainingDistance
                if expectedDistance <= 0:
                    logError("SCROLL CRITICAL ERROR: expectedDistance <= 0 !!!",
                             logger=logger, verbose=verbose)
                    return
            # If we go upward, we just inverse the expected distance:
            if not down:
                expectedDistance = -expectedDistance
            # And we execute it:
            executeScroll(driver, expectedDistance)
            # Now we sleep a little bit:
            randomSleep(sleepMin, sleepMax)
        # Next we get infos:
        (scrollTop, scrollBottom, windowHeight, documentHeight) = getPageInfos(driver)
        if scrollTop < minScrollTopReached:
            minScrollTopReached = scrollTop
        if scrollBottom > maxScrollBottomReached:
            maxScrollBottomReached = scrollBottom
        totalDistance = (maxScrollBottomReached - windowHeight) - minScrollTopReached
        # And if we reached the bottom of the page:
        if down and stopAtBorder and maxScrollBottomReached >= documentHeight:
            return
        # Or if we reach the top:
        elif not down and stopAtBorder and minScrollTopReached == 0:
            return
        # If we traveled the desired distance, we can stop:
        if distance is not None and totalDistance >= distance:
            return
        # If the document didn't changed since n, we stop:
        if stopWhenDocHeightNotChangedSince is not None and stopWhenDocHeightNotChangedSince > 0.0:
            # If we already reached the border to reach:
            if (down and maxScrollBottomReached >= documentHeight) or \
                (not down and minScrollTopReached == 0):
                # If the document height changed:
                if previousDocumentHeight != documentHeight:
                    previousDocumentHeight = documentHeight
                    previousDocumentHeightTimestamp = time.time()
                # Else we stop if it was too long:
                else:
                    currentTimestamp = time.time()
                    if currentTimestamp - previousDocumentHeightTimestamp >= stopWhenDocHeightNotChangedSince:
                        return
        # Here we check if we took too much time:
        if time.time() - startTime > timeout:
            logError("SCROLL CRITICAL ERROR: The scroll took too much time!", logger=logger, verbose=verbose)
            return
        # We check if there is a strange behavior:
        if previousScrollTop - scrollTop == 0:
            if maxScrollBottomReached < documentHeight:
                logError("SCROLL CRITICAL ERROR: We didn't move while it remains content downwards, it is very strange...",
                         logger=logger, verbose=verbose)
                return
        # If we didn't move or if the prob say "you can reverse scroll":
        if previousScrollTop - scrollTop == 0 or \
        (
            reverseScrollProb > 0.0 and \
            getRandomFloat() < reverseScrollProb and \
            totalDistance - traveledDistanceSincePreviousReverseScroll > reverseScrollEachTraveledDistance
        ):
            # We reset the traveled distance since previous reverse scroll:
            traveledDistanceSincePreviousReverseScroll = totalDistance
            # We set a certain distance to scroll:
            currentReverseScrollDistance = reverseScrollDistance
            # To be sure to don't scroll top too much:
            if currentReverseScrollDistance > 8000:
                logError("reverseScrollDistance is very high (" + str(reverseScrollDistance) + ")",
                         logger=logger, verbose=verbose)
                currentReverseScrollDistance = 8000
            currentReverseScrollDistance = getRandomInt \
            (
                int(currentReverseScrollDistance - randomGapRatio * currentReverseScrollDistance),
                int(currentReverseScrollDistance + randomGapRatio * currentReverseScrollDistance)
            )
            # Now we can reverse scroll:
            smartScroll \
            (
                driver,
                stopFunct=None, # We don't use any stop funct
                distance=currentReverseScrollDistance, # And we set a little random distance
                sequence=100,
                stopAtBorder=True, # If we reach the top, we stop
                distancePerSecond=distancePerSecond, # The same speed
                logger=logger,
                verbose=verbose,
                down=not down, # The reverse direction
                timeout=3, # To ensure we finish
                reverseScrollProb=0.0, # We do not reverse scroll in a reverse scroll...
            )
            # And finally we update all infos:
            (scrollTop, scrollBottom, windowHeight, documentHeight) = getPageInfos(driver)
            if scrollTop < minScrollTopReached:
                minScrollTopReached = scrollTop
            if scrollBottom > maxScrollBottomReached:
                maxScrollBottomReached = scrollBottom
            totalDistance = (maxScrollBottomReached - windowHeight) - minScrollTopReached



def testScrollTo():
    b = Browser(driverType=DRIVER_TYPE.chrome, proxy=None, useFastError404Detection=True)
    b.setWindowSize(1600, 1000)
    b.setWindowPosition(5, 500)
    startUrl = "file:///home/hayj/Drive/Workspace/Python/Crawling/Scroller/scroller/scroll-to-test.html"
    b.get(startUrl)
    allLetters = []
    for letter in ["a", "b", "c", "d", "e"]:
        allLetters.append(b.driver.find_element_by_css_selector("#" + letter))
    random.seed(0)
    for i in range(20):
        element = random.choice(allLetters)
        print("scrolling to " + element.text)
        scrollTo(b.driver, element, distancePerSecond=20000)
        time.sleep(0.1)
    b.close()

def testScrollTo2():
    b = Browser(driverType=DRIVER_TYPE.chrome, proxy=None, useFastError404Detection=True)
    b.setWindowSize(1600, 1000)
    b.setWindowPosition(5, 500)
    startUrl = "file:///home/hayj/Drive/Workspace/Python/Crawling/Scroller/scroller/scroll-to-test.html"
    b.get(startUrl)
    allLetters = []
    for letter in ["a", "a2"]:
        allLetters.append(b.driver.find_element_by_css_selector("#" + letter))
    random.seed(0)
    for i in range(20):
        element = random.choice(allLetters)
        print("scrolling to " + element.text)
        scrollTo(b.driver, element, distancePerSecond=1000)
        time.sleep(2.0)
    b.close()

def smartScrollTest1():
    proxy = getProxiesTest()[0]
    b = Browser(driverType=DRIVER_TYPE.chrome, proxy=proxy, useFastError404Detection=True)
    b.setWindowSize(1600, 1000)
    b.setWindowPosition(5, 500)
    url = "file://" + "/home/hayj/Drive/Workspace/Python/Crawling/Scroller/scroller/scroll-ajaxtest.html"
    b.get(url)
    smartScroll \
    (
        b,
        stopFunct=None,
        distance=10000000,
        sequence=100,
        stopAtBorder=False,
        distancePerSecond=1000,
        down=True,
        timeout=300,
        reverseScrollProb=0.1,
        reverseScrollDistance=None,
        reverseScrollEachTraveledDistance=50000,
    )
    b.close()

if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get("https://github.com/hayj/Scroller/blob/master/scroller/scroller.py")
    smartScroll(driver, stopAtBorder=True, humanBreaks=True, distancePerSecond=5000)



















# def test2():
#     print("START")
#     b = Browser(driverType=DRIVER_TYPE.chrome, headless=False, useFastError404Detection=True, ajaxSleep=0.2)
#     b.html("file://" + execDir(__file__) + "/scroll-ajaxtest.html")
#     def stopFunct(b, **kwargs):
#         printLTS(kwargs)
# #         if getRandomFloat() > 0.95:
# #             return True
#         return False
#     scroll(b, stopFunct=stopFunct, fast=True, stopAtBottom=False)
#     # Other examples:
# #     scroll(b, distance=2000 * 100, stopAtBottom=True, stopFunct=stopFunct, scrollerParams={"dataDirectory": dataDir() + "/Misc/crawling/scrolling"})
#     print("END")


# SCROLL_TYPE = Enum("SCROLL_TYPE", "human humanFast continuous teleportation")
# def scroll(driver, scrollType=SCROLL_TYPE.continuous, *args, **kwargs):
#     """
#         The only way to scroll on selenium is to send js script
#         But when you load a very long page (for instance you scroll
#         down infinite on Twitter), you have a lot of js usage so the
#         scroll become slow, the script is executed after a long time...
#         Because video and GIF and other things take a lot of js ressources.
#         So the it's better to user continuous scroll because it "jump"
#         to the right distance if it take too much time.
#         But phantomjs is faster than chrome for this task...
#     """
#     print("DEPRECATED")
#     if scrollType == SCROLL_TYPE.human:
#         humanScroll(driver, fast=False, *args, **kwargs)
#     elif scrollType == SCROLL_TYPE.humanFast:
#         humanScroll(driver, fast=True, *args, **kwargs)
#     elif scrollType == SCROLL_TYPE.continuous:
#         continuousScroll(driver, *args, **kwargs)
#     elif scrollType == SCROLL_TYPE.teleportation:
#         raise Exception("NOT YET IMPLEMENTED")

# def continuousScroll \
# (
#     driver,
#     stopFunct=None,
#     distance=10000000,
#     sequence=50,
#     stopAtBottom=False,
#     stopAtTop=True,
#     distancePerSecond=5000,
#     sleepMin=0.0001,
#     sleepMax=0.002,
#     randomGapRatio=0.2,
#     down=True,
#     maxDidntScroll=500,
#     logger=None,
#     verbose=True,
# #     allowUpwardScroll=True,
# ):
#     """
#         You must give distance > 0 and set down as False if you want to go down top
#     """
#     print("DEPRECATED")
#     log("DEPRECATED", logger=logger, verbose=True)
#     exit()
#     distance = abs(distance)
#     if isinstance(driver, Browser):
#         driver = driver.driver
#     (scrollTop, scrollBottom, windowHeight, documentHeight) = getPageInfos(driver)
#     scrollTopStart = scrollTop
#     totalDistance = 0
#     started = False
#     weDidntScrollSince = 0
# #     previousScrollTopForUpwardScroll = None
#     while scrollContinueCondition \
#     (
#         started,
#         stopFunct,
#         driver,
#         totalDistance,
#         scrollTop,
#         scrollBottom,
#         distance,
#     ):
# #         if started and allowUpwardScroll and down:
# #             pass
#         started = True
#         previousTimestamp = time.time()
#         for i in range(sequence):
#             timeSpent = time.time() - previousTimestamp
#             previousTimestamp = time.time()
#             expectedDistance = distancePerSecond * timeSpent
#             expectedDistance = getRandomInt(int(expectedDistance - randomGapRatio * expectedDistance),
#                                             int(expectedDistance + randomGapRatio * expectedDistance))
#             (scrollTop, scrollBottom, windowHeight, documentHeight) = getPageInfos(driver)
#             remainingDistance = distance - abs(scrollTopStart - scrollTop)
#             if remainingDistance < expectedDistance:
#                 expectedDistance = remainingDistance
#             if not down:
#                 expectedDistance = -expectedDistance
#             if (down and scrollBottom < documentHeight) or (not down and scrollTop > 0):
#                 if expectedDistance == 0:
#                     weDidntScrollSince += 1
#                 else:
#                     executeScroll(driver, expectedDistance)
#                     totalDistance += abs(expectedDistance)
#                     weDidntScrollSince = 0
#             else:
#                 weDidntScrollSince += 1
#             (scrollTop, scrollBottom, windowHeight, documentHeight) = getPageInfos(driver)
#             # We check if we are on the end of page:
#             if down and stopAtBottom:
#                 if scrollBottom == documentHeight:
#                     return
#             if not down and stopAtTop:
#                 if scrollTop <= 0:
#                     return
#             if weDidntScrollSince > maxDidntScroll:
#                 logError("SCROLL ERROR It's been a long time we didn't scroll...", logger=logger, verbose=verbose)
#                 return
#             randomSleep(sleepMin, sleepMax)
#             (scrollTop, scrollBottom, windowHeight, documentHeight) = getPageInfos(driver)
#
#
# def humanScroll(driver, stopFunct=None, distance=10000000, sequence=100, stopAtBottom=False, *args, **kwargs):
#     """
#         driver param can be webcrawler.browser.Browser or a Selenium driver
#         distance is the max distance
#         sequence is the number of scroll to send between each stopFunct call
#         stopFunct is a function which must return True if you want to stop the scrolling
#         this function take the browser (or driver) in parameters
#         stopAtBottom will stop the scroll if coordinates doesn't change between 2 scroll action. If you have ajax load, set stopAtBottom as False
#     """
#     print("DEPRECATED")
#     if isinstance(driver, Browser):
#         driver = driver.driver
#     scroller = iter(Scroller(*args, **kwargs))
#     (scrollTop, scrollBottom, windowHeight, documentHeight) = getPageInfos(driver)
#     minScrollTopReached = scrollTop
#     maxScrollBottomReached = scrollBottom
#     totalDistance = 0
#     previousScrollY = -1000
#     # While (we don't have stop action or we have one but we don't stop yet) and we didn't walk too much:
#     started = False
#     durationQueueSize = 150
#     durationQueue = NumberQueue(durationQueueSize)
#     while \
#     (
#         (
#             not started
#             or stopFunct is None
#             or not stopFunct(driver,
#                              totalDistance=totalDistance,
#                              minScrollTopReached=minScrollTopReached,
#                              maxScrollBottomReached=maxScrollBottomReached)
#         )
#         and abs(totalDistance) < distance
#     ):
#         started = True
#         previousTimestamp = None
#         for i in range(sequence):
#             # We get the scroll current data:
#             newScroll = next(scroller)
#             # We first sleep, but we don't sleep too much,
#             # we have to check the previous scrool timestamp:
#             duration = newScroll["duration"]
#             if previousTimestamp is not None:
#                 timeSpent = time.time() - previousTimestamp
#                 duration -= timeSpent
#                 durationQueue.add(duration)
#                 meanDuration = durationQueue.mean()
#                 # We log something if the human scroll become very slow:
#                 if durationQueue.index % durationQueueSize == 0:
#                     if meanDuration < 0:
#                         log("The human scroll become very slow, the delay is " + str(meanDuration) + " seconds!")
#                     else:
#                         log("OKKKKKKKKKKKK")
#                 if duration < 0:
#                     duration = 0
#                 print(duration)
#             time.sleep(duration)
#             previousTimestamp = time.time()
#             # And then we scroll:
#             executeScroll(driver, newScroll["distance"])
#             # We get new data:
#             (scrollTop, scrollBottom, windowHeight, documentHeight) = getPageInfos(driver)
#             # We check if we are on the end of page:
#             if stopAtBottom:
#                 if scrollBottom == documentHeight:
#                     return
#             # Then we update min and max scrolls:
#             if scrollTop < minScrollTopReached:
#                 minScrollTopReached = scrollTop
#             if scrollBottom > maxScrollBottomReached:
#                 maxScrollBottomReached = scrollBottom
#             # We inc the counter:
#             totalDistance += newScroll["distance"]
#
#
# class Scroller:
#     def __init__ \
#     (
#         self,
#         dataDirectory=None,
#         down=True,
#         randomize=True,
#         randomizeMax=0.2,
#         filePattern=None,
#         logger=None,
#         verbose=True,
#         fast=False,
#     ):
#         """
#             By default the function will take a random scroll file
#         """
#         print("DEPRECATED")
#         # Store all data:
#         self.logger = logger
#         self.verbose = verbose
#         self.down = down
#         self.randomize = randomize
#         self.randomizeMax = randomizeMax
#         # We get all lines:
#         self.filePattern = filePattern
#         if self.filePattern is None:
#             self.filePattern = "scrolldata-*"
#             if fast:
#                 self.filePattern = self.filePattern + "-fast"
#             self.filePattern = self.filePattern + ".txt"
#         self.dataDirectory = dataDirectory
#         if self.dataDirectory is None:
#             self.dataDirectory = dataDir() + "/Misc/crawling/scrolling"
#         try:
#             self.filePath = random.choice(sortedGlob(self.dataDirectory + "/" + self.filePattern))
#         except Exception as e:
#             logException(e, self, location="Scroller __init__")
#             raise Exception("No scrolling data found!")
#
#     def generateData(self):
#         # We parse all lines:
#         fileText = fileToStr(self.filePath)
#         scrollData = []
#         fileText = fileText.strip()
#         fileText = fileText.split("\n")
#         for current in fileText:
#             current = current.split(" ")
#             assert len(current[0]) > 0
#             assert len(current[1]) > 0
#             distance = int(current[0])
#             duration = float(current[1])
#             scrollData.append({"distance": distance, "duration": duration})
#         # We inverse the direction:
#         if not self.down:
#             for current in scrollData:
#                 current["distance"] = -current["distance"]
#         # We randomize all values:
#         if self.randomize:
#             for current in scrollData:
#                 for key in ["distance", "duration"]:
#                     value = current[key]
#                     variation = self.randomizeMax * abs(value)
#                     variation = getRandomFloat(-variation, variation)
#                     newValue = value + variation
#                     current[key] = newValue
#                 # We re-cast the distance to int:
#                 current["distance"] = round(current["distance"])
#             # Then we replace each 0 by a random value:
#             for current in scrollData:
#                 if current["distance"] == 0:
#                     current["distance"] = 1
#                 if current["duration"] == 0.0:
#                     current["duration"] = getRandomFloat(0.01, 0.03)
#         # We convert all duration in seconds:
#         for current in scrollData:
#             current["duration"] /= 1000
#         return scrollData
#
#     def __iter__(self):
#         # We infinitely yield the same data profile:
#         while True:
#             scrollData = self.generateData()
#             for current in scrollData:
#                 yield current
#
# def test1():
#     for current in Scroller():
#         printLTS(current)
#         break



