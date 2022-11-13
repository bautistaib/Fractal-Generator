#We aim to make an application that generates a fractal given a complex function with two variables, z and c. It will be parallelized with cupy.

import numpy as np
import cupy as cp
from time import time
import matplotlib.pyplot as plt
import PySimpleGUI as sg
import PIL
import io


def mandelbrot(z,c):
    z = z**2 + c
    return z



def fractal_gpu(func, max_iters = 50, max_abs = 2, x_min = -1.5, x_max = 1.5, y_min = -1.5, y_max = 1.5, resolution = 1000, z0 = 0):
    z = z0*cp.ones((resolution, resolution), dtype=cp.complex128)
    x, y = cp.ogrid[x_min:x_max:resolution*1j, y_max:y_min:resolution*1j]
    c = x + y*1j
    t0 = time()
    for i in range(max_iters):
        mask = cp.absolute(z) <= max_abs
        z[mask] = func(z[mask], c[mask])
    print("Fractal generated in %.2f seconds." % (time() - t0))
    return z




def plot_fractal(z):
    fig, ax = plt.subplots(figsize=(8,8))
    ax.imshow(cp.asnumpy(cp.log(cp.abs(z.T))), cmap = 'hot')
    #ax.imshow(np.angle(z.T), cmap = 'hsv', alpha = 0.5)
    ax.set_axis_off()
    plt.show()
    



def exp_kernel(z, c):
    return cp.exp(z) + c

def log_exp(z, c):
    return cp.log(cp.exp(z) + c)

def mandelbrot_var(z,c):
    return z**2 + c + z*c



def string_to_function(string):
    string = 'import cupy as cp\ngolden = (1+cp.sqrt(5))/2\ndef func(z, c): return '+ string
    d = {}
    exec(string, d)
    return d['func']
resolution = 800




def fractal_to_PIL(z, log = False):
    z = cp.absolute(z)
    if log:
        z = cp.log(z+1)
    z = cp.asnumpy(cp.absolute(z))
    z = z - z.min()
    z = z / z.max()
    z = z * 255
    z = z.astype(np.uint8)
    z = PIL.Image.fromarray(z)
    return z





def exponential(z):
    return cp.exp(z)


resolution = 700
window = sg.Window('Fractal')
center = sg.InputText('0,0', size=(40,1), tooltip='center of the graph', key='center')
width = sg.InputText('2', size=(40,1), tooltip='width of the graph', key='width')
button = sg.Button('Generate Fractal', key='generate')
button2 = sg.Button('Set center and width', key='corners_button')
function_field = sg.Multiline('z**2 + c', size=(40,1), key='function')
center_value = np.array([0.0,0.0])
width_value = 2.0
bottom_left = tuple(center_value - width_value/2)
top_right = tuple(center_value + width_value/2)
img = sg.Graph(canvas_size=(700,700), graph_bottom_left = bottom_left, float_values=True, graph_top_right=top_right, key='image',drag_submits=True, enable_events=True)
reference_check = False

x_min = bottom_left[0]
x_max = top_right[0]
y_min = bottom_left[1]
y_max = top_right[1]
#we create zoom in and zoom out buttons, with a textbox to let the user enter the zoom factor.

zoom_box = sg.InputText('10', size=(40,1), key='zoom_text')
zoom_in = sg.Button('Zoom in', key='zoom_in')
zoom_out = sg.Button('Zoom out', key='zoom_out')

#we add a checklist asking for logarithmic scale.
log_check = sg.Checkbox('Logarithmic scale', key='log_check')


max_iters_textbox = sg.InputText('50', size=(40,1), key='max_iters', tooltip='Maximum number of iterations')
max_abs_textbox = sg.InputText('10', size=(40,1), key='max_abs', tooltip='Maximum absolute value of z')
resolution_textbox = sg.InputText('5000', size=(40,1), key='resolution', tooltip='Resolution of the fractal')
z0_textbox = sg.InputText('0.5+0.25j', size=(20,1), key='z0', tooltip='Initial value of z')
save_paramerers_button = sg.Button('Save parameters', key='save_parameters')
reference_button = sg.Button('Toggle Center reference', key='reference_button')
layout = [[img], [button, function_field, log_check, reference_button], [button2, center, width], [zoom_in, zoom_out, zoom_box], [max_iters_textbox, max_abs_textbox, resolution_textbox, z0_textbox, save_paramerers_button]]
window.Layout(layout)

#we now create another window to let the user change the parameters of the fractal.

max_iters = 50
max_abs = 10
resolution = 5000


z0 = 0+0j
event = 'start'
while True:
    previous_event = event
    event, values = window.Read()
    #print('previous_event = {}, event = {}, values = {}'.format(previous_event, event, values))
    if event is None:
        break
    if event == 'generate':
        function = string_to_function(values['function'])
        z = fractal_gpu(function, max_iters = max_iters, max_abs = max_abs, x_min = x_min, x_max = x_max, y_min = y_min, y_max = y_max, resolution = resolution, z0 = z0)
        z = fractal_to_PIL(z.T, log = values['log_check'])
        z.thumbnail((700, 700))
        bio = io.BytesIO()
        z.save(bio, format="PNG")
        img.change_coordinates(bottom_left, top_right)
        img.erase()
        img.draw_image(data = bio.getvalue(), location = (x_min, y_max))
        if reference_check:
            reference_id = img.draw_point(tuple(center_value), size=width_value/200, color='red')
        img.Update(visible=True)
    if event == 'corners_button':
        center_value = np.array(values['center'].split(','), dtype=np.float64)
        width_value = np.float64(values['width'])
        bottom_left = tuple(center_value - width_value/2)
        top_right = tuple(center_value + width_value/2)
        x_min = bottom_left[0]
        x_max = top_right[0]
        y_min = bottom_left[1]
        y_max = top_right[1]
        z = fractal_gpu(function, max_iters = max_iters, max_abs = max_abs, x_min = x_min, x_max = x_max, y_min = y_min, y_max = y_max, resolution = resolution, z0 = z0) 
        z = fractal_to_PIL(z.T, log = values['log_check'])
        z.thumbnail((700, 700))
        bio = io.BytesIO()
        z.save(bio, format="PNG")
        img.change_coordinates(bottom_left, top_right)
        img.erase()
        img.draw_image(data = bio.getvalue(), location = (x_min, y_max))
        if reference_check:
            reference_id = img.draw_point(tuple(center_value), size=width_value/200, color='red')
        img.Update(visible=True)
    if event == 'image':
        pos = values['image']
        if id == None:
            id = img.draw_point(pos, size=1, color='red')
        img.delete_figure(id)
        id = img.draw_text(text='{:.3f} + {:.3f} i'.format(pos[0], pos[1]), location = (pos[0], pos[1]+ width_value/25), color='red')
        if previous_event == 'image':
            continue
        else:
            pos_ini = values['image']
    if event == 'image+UP':
        pos_fin = values['image']
        center_value -= np.array(pos_fin, dtype = np.float64) - np.array(pos_ini, dtype = np.float64)
        bottom_left = tuple(center_value - width_value/2)
        top_right = tuple(center_value + width_value/2)
        x_min = bottom_left[0]
        x_max = top_right[0]
        y_min = bottom_left[1]
        y_max = top_right[1]
        img.delete_figure(id)
        img.Update(visible=True)
        z = fractal_gpu(function, max_iters = max_iters, max_abs = max_abs, x_min = x_min, x_max = x_max, y_min = y_min, y_max = y_max, resolution = resolution, z0 = z0)
        z = fractal_to_PIL(z.T, log = values['log_check'])
        z.thumbnail((700, 700))
        bio = io.BytesIO()
        z.save(bio, format="PNG")
        img.change_coordinates(bottom_left, top_right)
        img.erase()
        img.draw_image(data = bio.getvalue(), location = (x_min, y_max))
        if reference_check:
            reference_id = img.draw_point(tuple(center_value), size=width_value/200, color='red')
        img.set_tooltip(None)
        img.Update(visible=True)
    if event == 'zoom_in':
        zoom_factor = float(values['zoom_text'])
        width_value /= zoom_factor
        bottom_left = tuple(center_value - width_value/2)
        top_right = tuple(center_value + width_value/2)
        x_min = bottom_left[0]
        x_max = top_right[0]
        y_min = bottom_left[1]
        y_max = top_right[1]
        z = fractal_gpu(function, max_iters = max_iters, max_abs = max_abs, x_min = x_min, x_max = x_max, y_min = y_min, y_max = y_max, resolution = resolution, z0 = z0)
        z = fractal_to_PIL(z.T, log = values['log_check'])
        z.thumbnail((700, 700))
        bio = io.BytesIO()
        z.save(bio, format="PNG")
        img.change_coordinates(bottom_left, top_right)
        img.erase()
        img.draw_image(data = bio.getvalue(), location = (x_min, y_max))
        if reference_check:
            reference_id = img.draw_point(tuple(center_value), size=width_value/200, color='red')
        img.Update(visible=True)
    if event =='zoom_out':
        zoom_factor = float(values['zoom_text'])
        width_value *= zoom_factor
        bottom_left = tuple(center_value - width_value/2)
        top_right = tuple(center_value + width_value/2)
        x_min = bottom_left[0]
        x_max = top_right[0]
        y_min = bottom_left[1]
        y_max = top_right[1]
        z = fractal_gpu(function, max_iters = max_iters, max_abs = max_abs, x_min = x_min, x_max = x_max, y_min = y_min, y_max = y_max, resolution = resolution, z0 = z0)
        z = fractal_to_PIL(z.T, log = values['log_check'])
        z.thumbnail((700, 700))
        bio = io.BytesIO()
        z.save(bio, format="PNG")
        img.change_coordinates(bottom_left, top_right)
        img.erase()
        img.draw_image(data = bio.getvalue(), location = (x_min, y_max))
        if reference_check:
            reference_id = img.draw_point(tuple(center_value), size=width_value/200, color='red')
        img.Update(visible=True)
    if event == 'save_parameters':
        max_iters = int(values['max_iters'])
        max_abs = float(values['max_abs'])
        resolution = int(values['resolution'])
        z0 = complex(values['z0'])
    if event == 'reference_button':
        if not reference_check:
            reference_check = True
            reference_id = img.draw_point(tuple(center_value), size=width_value/200, color='red')
        else:
            reference_check = False
            img.delete_figure(reference_id)
            reference_id = None
window.Close()