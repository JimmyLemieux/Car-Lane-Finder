# Car-Lane-Finder
The use of Canny Edge Detection and houghLines made this project possible. This project introduced me to the use of numpy arrays and working with vectors that are in space. The motivation behind this project was to make a self driving car in a video game.

# initialization
The first thing that needs to be done is to set up a capturebox in the top-left corner of the screen. This is where either the video game screen would go or a test video. The screen is loaded into a numpy array. The contents of this array are the pixels in that certain screen region. Then a quit command was made for user experience. The processImage Function is where the screen is processed to provide the most efficient and clean way for edges to be detected in the region.
 ```python
 def main():
	timer(2)
	while 1:
		screen = np.array(ImageGrab.grab(bbox=(0,40,800,600)))
		screen = processImage(screen)
		cv2.imshow('window',screen)
		cv2.setMouseCallback('window',draw_circle)
		if cv2.waitKey(25) & 0xFF == ord('q'):
			cv2.destroyAllWindows()
			break
 ```
 # Image Processing
  The image processing is used in order to make the Canny Edge detection the smoothest and most reliable. The first thing I chose to do is instantiate the white and yellow colors (Due to the fact that these are common colors for lines on a road). The image was then converted into greyscale to see the difference in hues clearer. The Guassian Blur gives the effect of the lines and shapes not being as sharp and thin. Thus making it easier to detect.
  ```python
  def processImage(org_screen):
	org_screen = color_selection(org_screen)
	org_screen = cv2.cvtColor(org_screen,cv2.COLOR_BGR2GRAY)
	org_screen = cv2.GaussianBlur(org_screen, (5,5), 0)
	org_screen = cv2.Canny(org_screen,50,160)	#Edge detection applied
  ```
  *The color selection method*
  ```python
  def color_selection(screen):
	hls = cv2.cvtColor(screen,cv2.COLOR_RGB2HLS)
	lower_white = np.uint8([20,200,0])
	upper_white = np.uint8([255,255,255])
	#Now make a range for the white color
	white_color = cv2.inRange(hls,lower_white,upper_white)

	lower_yellow = np.uint8([10,50,100])
	upper_yellow = np.uint8([100,255,255])

	#Make the range for the yellow color
	yellow_color = cv2.inRange(hls,lower_yellow,upper_yellow)

	comb = cv2.bitwise_or(white_color,yellow_color)
	return cv2.bitwise_and(screen, screen, mask = comb)
  ```
  
  In order to reduce the amount of random line in the scene a region of interest was constructed to make the view only focused on the lines of the road. Example Image of the ROI:
  ![ROI](https://i.gyazo.com/d553dce45582b665700a5ea79ed6815e.png)
*The vertices are initiated in a numpy array*
```python
  vertices = np.array([[107,492],[382,343],[458,352],[720,491]])
	org_screen = roi(org_screen,vertices)
  
  def roi(screen, vertices):
	mask = np.zeros_like(screen,dtype=np.uint8)
	cv2.fillPoly(mask,np.int32([vertices]),255)
	masked_image = cv2.bitwise_and(screen, mask)
	return masked_image
```
# Hough Line Management
The in order To draw the best hough line on the edge detection the hough lines go through linear regression. In order to find the line of best fit between the numpy array of all of the data points in the hough line would be recorded in the numpy array. After a certain number of data point a best fil line is drawn from (x1,y1) starting points to (x2,y2) ending points.

```python
#A single indexed array that contains the end points of the line
xL = []
yL = []
xR = []
yR = []
nc = 0
def manage_lines(screen,lines):
	global xL
	global yL
	global xR
	global yR
	global nc
	nc += 1
	if nc % 25 == 0:xL,yL,xR,yR = reset_points(xL,yL,xR,yR)
	if nc == 1000:nc = 0
	for line in lines:
		for x1,y1,x2,y2 in line:
			slope = (y2 - y1)/(x2 - x1)
			if slope == -1:
			#Increasing x, decreasing y
				xL += [x1,x2]
				yL += [y1,y2]
				end,start = find_best_fit_left(xL,yL)
				cv2.line(screen,start,end,[255,255,255],3)
			elif slope == 0:
				xR += [x1,x2]
				yR += [y1,y2]
				end,start = find_best_fit_right(xR,yR)
				cv2.line(screen,start,end,[255,255,255],3)
```
*Linear regression and line of best fit calculations. These lines are extrapolate through the edges*
```python
#IF we know the line of best fir, can't we use linear regression to predict the next points (Extrapolate)

def find_best_fit_right(x,y):
#Based on the array of the points in the line
#Find the line of best fit
	fit = np.polyfit(x,y,1)
	#This simplifies the y=mx+b formula to only one variable
	f = np.poly1d(fit)
	#This fits the
	x_new = np.linspace(min(x),max(x),10).astype(int)
	print x_new, 'right'
	x_extrapolate = min(x_new) - 20
	y_new = f(x_new).astype(int) #Doing the equation y=mx+b
	y_new_extrapolate = f(x_extrapolate).astype(int)
	points_new = list(zip(x_new,y_new))
	return (x_extrapolate,y_new_extrapolate),max(points_new)

def find_best_fit_left(x,y):
	fit = np.polyfit(x,y,1)
	f = np.poly1d(fit)
	x_new = np.linspace(min(x),max(x),10).astype(int)
	print x_new, 'left'
	x_extrapolate = max(x_new) + 20
	y_new = f(x_new).astype(int)
	y_new_extrapolate = f(x_extrapolate).astype(int)
	points_new = list(zip(x_new,y_new))
	#
	return (x_extrapolate,y_new_extrapolate), min(points_new)
  ```
  # Limitations
  *This is an example of a curved road*
  ![example](https://i.gyazo.com/612b802cc5dc57b7114cbbb356321aa7.png)
  With this example of the curved road you can see that the right lane line is not extrapolating properly. The hough line should be able to cover the rest of the line. This bug may be due to the trivial way I am computing the line of best fit.
  # Next Steps
  *I plan to pick up this project later and add parabolic functions to the line to create a curvature following the line*
  
  
