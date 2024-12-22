from NeditGD import Object, Editor
from trigger_ids import TRIGGER_TO_ID, TRIGGER_RELATED_TO_ID
from weights import *
import random

level = Editor.load_current_level()

# constants
group_reset = 999
layer_modifier = 1000
layer_spacing = [0, 60, 0, 160, 0, 520, 0, 920]
activation_group = 800
toggle_draw = 994
toggle_draw2 = 922


# Converts coordinates based on the editor grid to the actual editor coordinates (it's bugged)
def set_location(object, x, y):
    object.x = int(x * 30 + 15)
    object.y = int(y * 30 - 15)


# Determines which itemId a node should have depending on its layer, output shape, channel, i and j coordinates.
def findId(layer, shape, c, i, j):
    return layer * layer_modifier + c * shape[2] * shape[1] + j * shape[2] + i + 1


# creates a counter on time mode
def create_node(itemid):
    node = Object(id=TRIGGER_RELATED_TO_ID['counter'])
    node.item_id = itemid
    node.timer_display = 1
    return node


# calculates: itemid2 = itemid2 + itemid1 * weight
def create_connection(itemid1, itemid2, weight):
    trigger = Object(id=TRIGGER_TO_ID['item_edit'])
    trigger.spawn_triggered = 1
    trigger.multi_trigger = 1
    trigger.item_id = itemid1
    trigger.target = itemid2
    trigger.num_mod = weight
    trigger.item_type_2 = 2
    trigger.item_type_3 = 2
    trigger.num_op_1 = 1
    trigger.item_type_1 = 2
    return trigger


# Adds bias to itemid
# The bias is just a fancy word for the starting value of the itemid
def create_bias(itemid, bias):
    trigger = Object(id=TRIGGER_TO_ID['item_edit'])
    trigger.spawn_triggered = 1
    trigger.multi_trigger = 1
    trigger.target = itemid
    trigger.num_mod = bias
    trigger.item_type_3 = 2
    trigger.num_op_1 = 1
    return trigger


# Creates the screen used to draw numbers
def create_screen(width, height, xoffset, yoffset):
    for j in range(height):
        for i in range(width):
            # building the toggle on
            toggle = Object(id=TRIGGER_TO_ID['toggle'])
            toggle.editor_layer_1 = 1
            set_location(toggle, xoffset + i, yoffset + height - j)
            toggle.target = j * height + i + 1
            toggle.touch_triggered = 1
            toggle.multi_trigger = 1
            toggle.activate_group = 1
            toggle.groups = [toggle_draw, toggle_draw2]
            level.add_object(toggle, mark_as_scripted=False)

            # building the toggle off
            toggle = Object(id=TRIGGER_TO_ID['toggle'])
            toggle.editor_layer_1 = 2
            set_location(toggle, xoffset + i, yoffset + height - j)
            toggle.target = j * height + i + 1
            toggle.spawn_triggered = 1
            toggle.multi_trigger = 1
            toggle.groups = [group_reset]
            level.add_object(toggle, mark_as_scripted=False)

            # building the pixel being toggled
            pixel = Object(id=211)
            pixel.editor_layer_1 = 3
            set_location(pixel, xoffset + i, yoffset + height - j)
            pixel.groups = [j * height + i + 1]
            level.add_object(pixel, mark_as_scripted=False)

            # counter representation
            node = create_node(j * height + i + 1)
            node.editor_layer_1 = 0
            set_location(node, xoffset + i, yoffset + height - j + 30)
            level.add_object(node, mark_as_scripted=False)

            # set counter
            timer = Object(id=TRIGGER_TO_ID['time'])
            timer.editor_layer_1 = 4
            set_location(timer, xoffset + i, yoffset + height - j)
            timer.touch_triggered = 1
            timer.multi_trigger = 1
            timer.item_id = j * height + i + 1
            timer.timer_start = 1
            timer.timer_paused = 1
            timer.groups = [toggle_draw, toggle_draw2]
            level.add_object(timer, mark_as_scripted=False)

            # reset counter
            timer = Object(id=TRIGGER_TO_ID['time'])
            timer.editor_layer_1 = 5
            set_location(timer, xoffset + i, yoffset + height - j)
            timer.spawn_triggered = 1
            timer.multi_trigger = 1
            timer.item_id = j * height + i + 1
            timer.timer_start = 0
            timer.timer_paused = 1
            timer.groups = [group_reset]
            level.add_object(timer, mark_as_scripted=False)


#Used for debugging. It sets the screen to a particular image.
def set_hardcoded_image(image):
    for j in range(image.shape[1]):
        for i in range(image.shape[0]):
            pickup = Object(id=TRIGGER_TO_ID['pickup'])
            set_location(pickup, 3 + i, 100 + image.shape[1] - j)
            pickup.spawn_triggered = 1
            pickup.multi_trigger = 1
            pickup.item_id = j * image.shape[1] + i + 1
            pickup.count = int(image[j][i])
            pickup.override_count = 1
            pickup.groups = [998]
            level.add_object(pickup, mark_as_scripted=False)


#Creates a convolutional layer
def create_convolution(in_layer, in_shape, out_layer, out_shape, kernel, bias, stride=1, padding=1):

    def is_padding(i, j, dx, dy):
        if i + dx >= in_shape[1] or i + dx < 0:
            return True
        if j + dy >= in_shape[2] or j + dy < 0:
            return True
        return False

    # Build output layer and add bias
    for c in range(out_shape[0]):
        for j in range(out_shape[2]):
            for i in range(out_shape[1]):
                node = create_node(findId(out_layer, out_shape, c, i, j))
                node.editor_layer_1 = 0
                set_location(node, layer_spacing[out_layer] - 60 + i * 3, 100 + c * (out_shape[2] + 2) + out_shape[1] - j)
                level.add_object(node, mark_as_scripted=False)

                trigger = create_bias(findId(out_layer, out_shape, c, i, j), bias[c])
                trigger.groups = [activation_group + out_layer]
                set_location(trigger, layer_spacing[out_layer] - 30 + i, 100 + c * (out_shape[2] + 2) + out_shape[2] - j)
                level.add_object(trigger, mark_as_scripted=False)

    # Apply convolution
    for c_out in range(kernel.shape[0]):
        for c_in in range(kernel.shape[1]):
            for j_out, j in enumerate(range(1 - padding, in_shape[2] - 1 + padding, stride)):
                for i_out, i in enumerate(range(1 - padding, in_shape[1] - 1 + padding, stride)):
                    for dy in range(int(-(kernel.shape[2] - 1) / 2), int((kernel.shape[2] - 1) / 2 + 1)):
                        for dx in range(int(-(kernel.shape[3] - 1) / 2), int((kernel.shape[3] - 1) / 2 + 1)):
                            if is_padding(i, j, dx, dy):
                                continue
                            input_node = findId(in_layer, in_shape, c_in, i + dx, j + dy)
                            output_node = findId(out_layer, out_shape, c_out, i_out, j_out)
                            trigger = create_connection(input_node, output_node, kernel[c_out][c_in][dy+1][dx+1])
                            trigger.groups = [activation_group + out_layer]
                            set_location(trigger, layer_spacing[out_layer] + 30 + c_in * (in_shape[2] + 2) * 2 + 2 * i_out * stride + dx,
                                         100 + c_out * (in_shape[1] + 2) * 2 + 2 * j_out * stride + dy)
                            level.add_object(trigger, mark_as_scripted=False)

def create_maxpool(in_layer, in_shape, out_layer, out_shape, kernel, stride):
    pass

#Creates a linear layer that uses the outputs of a convolutional layer as it's inputs
def create_conv2linear(in_layer, in_shape, out_layer, out_count, weights, bias):
    # build output layer and add bias
    for o in range(out_count):
        node = create_node(out_layer * layer_modifier + o)
        set_location(node, layer_spacing[out_layer], 100 + o)
        level.add_object(node)
        trigger = create_bias(out_layer * layer_modifier + o, bias[o])
        set_location(trigger, layer_spacing[out_layer] - 1, 100 + o)
        trigger.groups = [activation_group + out_layer]
        level.add_object(trigger, mark_as_scripted=False)

    # add weights
    for o in range(out_count):
        for c in range(in_shape[0]):
            for j in range(in_shape[2]):
                for i in range(in_shape[1]):
                    input_node = findId(in_layer, in_shape, c, i, j)
                    output_node = out_layer * layer_modifier + o
                    weight = weights[o][c * in_shape[1] * in_shape[1] + j * in_shape[2] + i]
                    trigger = create_connection(input_node, output_node, weight)
                    trigger.groups = [activation_group + out_layer]
                    set_location(trigger, layer_spacing[out_layer] + o,
                                 100 + c * in_shape[1] * in_shape[1] + j * in_shape[1] + i)
                    level.add_object(trigger, mark_as_scripted=False)

# Performs relu on the outputs of a convolutional layer
def create_relu(layer, shape):
    def single_relu(itemid):
        compare = Object(id=TRIGGER_TO_ID['item_compare'])
        compare.spawn_triggered = 1
        compare.multi_trigger = 1
        compare.item_id = itemid
        compare.target = itemid
        compare.item_type_1 = 2
        compare.num_op_3 = 3
        compare.num_mod = 1
        compare.num_mod_2 = 0

        reset = Object(id=TRIGGER_TO_ID["time"])
        reset.spawn_triggered = 1
        reset.multi_trigger = 1
        reset.timer_paused = 1
        reset.item_id = itemid
        reset.groups = [itemid, group_reset]
        return compare, reset

    for c in range(shape[0]):
        for j in range(shape[2]):
            for i in range(shape[1]):
                comp, res = single_relu(findId(layer, shape, c, i, j))
                comp.groups = [activation_group + layer + 1]
                set_location(comp, layer_spacing[layer] + i * 3, 100 + c * (shape[1] + 2) + shape[1] - j)
                set_location(res, layer_spacing[layer] + i * 3 + 1, 100 + c * (shape[1] + 2) + shape[1] - j)
                level.add_object(comp, mark_as_scripted=False)
                level.add_object(res, mark_as_scripted=False)



#create_screen(28, 28, 3, 3)
#set_hardcoded_image(img1)

# Building the network
create_convolution(0, (1, 28, 28), 1, (10, 14, 14), kernel=conv1, bias=bias1, stride=2, padding=1)
create_relu(1, (10, 14, 14))
create_convolution(1, (10, 14, 14), 3, (20, 7, 7), kernel=conv2, bias=bias2, stride=2, padding=1)
create_relu(3, (20, 7, 7))
create_convolution(3, (20, 7, 7), 5, (20, 4, 4), kernel=conv3, bias=bias3, stride=2, padding=1)
create_relu(5, (20, 4, 4))
create_conv2linear(5, (20, 4, 4), 7, 10, weights=linear_w, bias=linear_b)

level.save_changes()