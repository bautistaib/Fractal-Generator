# Fractal-Generator
This is my first GUI proyect. A Mandelbrot-like fractal generator, defined by the iterative evaluation of a function of two complex variables. The interfece let you dinamically change the ploted region, as well as the fractal parameters.

**Requirements**

This program uses the cupy libraary, which needs CUDA to work. Make sure to follow the instructions in https://docs.cupy.dev/en/stable/install.html if you don't have it installed before you install the packages in the requirements.txt file

**Function**

![Captura](https://user-images.githubusercontent.com/36866639/201500854-fe45d1a7-2577-4a7b-b517-aa978374caeb.PNG)

The fractal can be moved in a click-and-drag fashion, as well as with the buttons below. The fractal will regenerate after each movement.

Image references:

1 - Here you write a function of two complex variables (that must be called 'z' and 'c) where z represents the output of the last iteration (by default set in zero, but changeable through the parameter 11), while c represents a point on the complex plane. The function must be on cupy format, for example, to use an exponential format it should be written as cp.exp(z)

2 - Set logarithmic scale for the plot. Usefull to get sharper edges when the allowed maximum absolute value of z is big or when rapidly incresing functions are used, such as the exponential function.

3 - Toggle a center marker to make easier to set an interesting point as the center for zoom.

4 - Regenerates the fractal using the coordinates and with of 5 and 6.

5 - The cartesian coordinates of the point you want to center the image after clicking in 4, with format x,y.

6 - The width on the complex plane that will be ploted on the image (e.g. a value of 2 centered in 0,0 will plot between -1 and 1).

7 - The amount of zoom you make with respect to the center after you press the zoom in/out buttons.

8 - Maximum number of iterations.

9 - Maximum absolute value allowed for z.

10 - Resolution of the image in pixels

11 - Initial value of z

To change the parameters in 8, 9, 10 and 11 you must press the "save parameters" button and then "generate fractal"
