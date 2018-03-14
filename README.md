
# Scroller

This tools can simulate human scrolling using randomize mechanism. The scroll using recorded human scroll is now deprecated.

## Install

You must install all dependencies in `wm-dist` and specify the data directory when you use the class or function

    pip install ./wm-dist/*.gz

So you just need to download the `wm-dist` dir.

Then you can import it using:

    from scroller.scroller import smartScroll, getPageInfos, scrollTo

## Function `smartScroll()`

### All features

You can set a scroll limit to the bottom and say to stop at bottom:

    smartScroll(seleniumDriver, distance=100000, stopAtBorder=True)

You can adjust the speed (pixel per seconds):

	smartScroll(seleniumDriver, distancePerSecond=1000)

You can give a function which say if the scroll have to stop:

	def stopFunct(driver,
	             totalDistance=None,
	             minScrollTopReached=None,
	             maxScrollBottomReached=None):
		# Here you can test if an element exists:
		soup = BeautifulSoup(driver.page_source, 'html.parser')
		element = soup.select_one("#target")
		if element is not None:
			return True # We stop
		return False # Else we continue

	smartScroll(seleniumDriver, stopFunct=stopFunct)

You can say to scroll down top:

	smartScroll(seleniumDriver, down=False)

You can set a timeout in second if you don't want to be blocked:

	smartScroll(seleniumDriver, timeout=200)

You can introduce human breaks behavior:

	smartScroll(seleniumDriver, humanBreaks=True)

### Full example

	def helloWorld():
	    driver = webdriver.Chrome()
	    driver.get("https://github.com/hayj/Scroller/blob/master/scroller/scroller.py")
	    smartScroll(driver, stopAtBorder=True, distancePerSecond=5000, humanBreaks=True)
	    print("DONE")

	if __name__ == "__main__":
	    helloWorld()

## Function `getPageInfos()`

This function take a driver and return (scrollTop, scrollBottom, windowHeight, documentHeight)

## Function `scrollTo(driver, element, *args, **kwargs)`

This function scroll to a Selenium element, you can give smartScroll args with *args, **kwargs