
# Scroller

This tools can simulate human scrolling using randomize mechanism. It takes a Selenium driver and scroll the current page. You can give a stop funct callback which is called at periodic intervals and have to return True to terminate the scroll, you can set the speed, set a timeout and so on.

	driver = webdriver.Chrome()
	driver.get("https://github.com/hayj/Scroller/blob/master/scroller/scroller.py")
	smartScroll(driver, stopAtBorder=True, distancePerSecond=5000, humanBreaks=True)

## Install

Install the scroller dist and its dependencies in `wm-dist`:

	git clone https://github.com/hayj/Scroller.git
	pip install ./Scroller/wm-dist/*.tar.gz

Then you can import it using:

    from scroller.scroller import smartScroll, getPageInfos, scrollTo

## Function `smartScroll(driver, ...)`

You can set a scroll limit to the bottom and say to stop at bottom:

    smartScroll(seleniumDriver, distance=100000, stopAtBorder=True)

You can adjust the speed (pixel per seconds):

	smartScroll(seleniumDriver, distancePerSecond=1000)

You can give a function which say if the scroll have to stop:

	def stopFunct(driver,
	             totalDistance=None,
	             minScrollTopReached=None,
	             maxScrollBottomReached=None):
		# Here for example you can test if an element exists:
		soup = BeautifulSoup(driver.page_source, 'html.parser')
		element = soup.select_one("#target")
		if element is not None:
			return True # We stop
		return False # Else we continue

	smartScroll(seleniumDriver, stopFunct=stopFunct)

You can set the direction of the scroll:

	smartScroll(seleniumDriver, down=False)

You can set a timeout in second if you don't want to be blocked:

	smartScroll(seleniumDriver, timeout=200)

You can introduce human breaks behavior (simulated):

	smartScroll(seleniumDriver, humanBreaks=True)

If you want to automatically stop when the page height not changed since n seconds, use `stopWhenDocHeightNotChangedSince`:

	smartScroll(seleniumDriver, stopWhenDocHeightNotChangedSince=10)

## Function `getPageInfos(driver)`

This function take a driver and return `(scrollTop, scrollBottom, windowHeight, documentHeight)`. You are at the bottom of the page if `scrollBottom >= documentHeight`.

## Function `scrollTo(driver, element, *args, **kwargs)`

This function scroll to a Selenium element, you can give smartScroll args with `*args, **kwargs`

## Function `moveTo(driver, element)`

This function move the mouse to the element.