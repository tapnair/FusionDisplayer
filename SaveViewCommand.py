import adsk.core
import adsk.fusion
import traceback

from .Fusion360Utilities.Fusion360Utilities import AppObjects, get_default_dir, read_settings, write_settings
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase

import json
import os
from collections import defaultdict


def make_point(point: adsk.core.Point3D):
    point_out = {
        "x": point.x,
        "y": point.y,
        "z": point.z

    }
    return point_out


def make_vector(vector: adsk.core.Vector3D):
    vector_out = {
        "x": vector.x,
        "y": vector.y,
        "z": vector.z

    }
    return vector_out


def get_point(point):
    vector_out = adsk.core.Point3D.create(
        point["x"],
        point["y"],
        point["z"]
    )
    return vector_out


def get_vector(vector):
    vector_out = adsk.core.Vector3D.create(
        vector["x"],
        vector["y"],
        vector["z"]
    )
    return vector_out


def set_camera(camera_object):
    ao = AppObjects()

    camera = ao.app.activeViewport.camera

    camera.cameraType = camera_object["camera_type"]
    camera.eye = get_point(camera_object["eye"])
    camera.isFitView = camera_object["is_fit_view"]
    camera.isSmoothTransition = camera_object["is_smooth"]
    camera.target = get_point(camera_object["target"])
    camera.upVector = get_vector(camera_object["up_vector"])
    camera.viewExtents = camera_object["view_extents"]
    camera.viewOrientation = camera_object["view_orientation"]

    if not camera_object["camera_type"] == adsk.core.CameraTypes.OrthographicCameraType:
        camera.perspectiveAngle = camera_object["perspective_angle"]

    ao.app.activeViewport.camera = camera


def build_camera_object():
    ao = AppObjects()
    camera = ao.app.activeViewport.camera

    camera_object = {

        "camera_type": camera.cameraType,
        "eye": make_point(camera.eye),
        "is_fit_view": camera.isFitView,
        "is_smooth": camera.isSmoothTransition,
        "target": make_point(camera.target),
        "up_vector": make_vector(camera.upVector),
        "view_extents": camera.viewExtents,
        "view_orientation": camera.viewOrientation
    }

    if not camera_object["camera_type"] == adsk.core.CameraTypes.OrthographicCameraType:
        camera_object["perspective_angle"] = camera.perspectiveAngle

    return camera_object


def build_parameter_object(all_params):
    ao = AppObjects()
    um = ao.units_manager

    design = ao.design

    if design is None:
        return None

    if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:

        if all_params:
            parameters = design.allParameters
        else:
            parameters = design.userParameters

        parameter_object = {}

        for parameter in parameters:
            parameter_object[parameter.name] = {
                "value": um.formatInternalValue(parameter.value, parameter.unit, False),
                "expression": parameter.expression,
                "dependants": True if parameter.dependentParameters.count > 0 else False,
                "unit": parameter.unit,
                "deletable": parameter.isDeletable
            }

        return parameter_object
    else:
        return False


def set_parameters(parameter_object):
    ao = AppObjects()
    um = ao.units_manager

    design = ao.design

    if design is None:
        return False

    if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:

        all_parameters = design.allParameters

        for parameter in all_parameters:

            this_parameter = parameter_object.get(parameter.name)
            if this_parameter is not None:
                unit_type = this_parameter.get("unit", "")

                if len(unit_type) > 0:

                    if um.isValidExpression(this_parameter["expression"], unit_type):
                        evaluated_value = um.evaluateExpression(this_parameter["expression"], unit_type)
                    else:
                        continue
                else:
                    evaluated_value = um.evaluateExpression(this_parameter["expression"])

                # TODO handle units with an attribute that is written on create.  Can be set for link
                if parameter.value != evaluated_value:
                    parameter.expression = this_parameter["expression"]
        return True

    else:
        return False


def build_display_state_object():
    ao = AppObjects()
    root_comp = ao.root_comp

    display_state_object = {}

    if root_comp is not None:

        all_occurrences = ao.root_comp.allOccurrences

        for occurrence in all_occurrences:
            display_state_object[occurrence.fullPathName] = occurrence.isLightBulbOn

    return display_state_object


def set_display_state(display_state_object):
    ao = AppObjects()
    root_comp = ao.root_comp

    if root_comp is None:
        return False

    all_occurrences = root_comp.allOccurrences

    for occurrence in all_occurrences:
        state = display_state_object.get(occurrence.fullPathName, None)

        if state is not None:
            occurrence.isLightBulbOn = state

    return True


def delete_view_attributes():
    ao = AppObjects()

    view_object_attributes = ao.document.attributes.itemsByGroup('displayer_custom_views')

    for attribute in view_object_attributes:
        attribute.deleteMe()


def delete_tooltips():
    ao = AppObjects()

    for custom_view_number in range(0, 10):
        command_defintion = ao.ui.commandDefinitions.itemById(
            'cmdID_SetViewCommand_' + str(custom_view_number)
        )
        command_defintion.tooltip = 'This View has not been set'
        command_defintion.controlDefinition.isEnabled = False


def delete_appearance_attributes():
    ao = AppObjects()

    appearance_object_attributes = ao.document.attributes.itemsByGroup('displayer_appearances')

    for attribute in appearance_object_attributes:
        attribute.deleteMe()


def remove_all_appearances():
    ao = AppObjects()
    all_appearances = ao.design.appearances

    for appearance in all_appearances:
        used_by = appearance.usedBy
        for item in used_by:
            item.appearance = None


def get_view_from_number(custom_view_number):
    ao = AppObjects()
    view_object_attribute = ao.document.attributes.itemByName(
        'displayer_custom_views',
        "Custom View " + str(custom_view_number)
    )
    if view_object_attribute is not None:
        view_object = json.loads(view_object_attribute.value)
    else:
        view_object = None

    return view_object


def refresh_custom_views():
    ao = AppObjects()
    view_object_attributes = ao.app.activeDocument.attributes.itemsByGroup('displayer_custom_views')

    delete_tooltips()

    for view_object_attribute in view_object_attributes:
        view_object = json.loads(view_object_attribute.value)
        command_defintion = ao.ui.commandDefinitions.itemById(
            'cmdID_SetViewCommand_' + view_object_attribute.name[-1:]
        )
        command_defintion.tooltip = view_object["name"]
        command_defintion.controlDefinition.isEnabled = True


def set_appearances(view_name):
    ao = AppObjects()
    attributes = ao.design.findAttributes("displayer_appearances", view_name)

    remove_all_appearances()

    if len(attributes) > 0:

        for attribute in attributes:
            item = attribute.parent

            if item is not None:
                item.appearance = ao.design.appearances.itemById(attribute.value)


def build_appearances(view_name):
    ao = AppObjects()
    all_appearances = ao.design.appearances
    for appearance in all_appearances:
        used_by = appearance.usedBy
        for item in used_by:

            item.attributes.add("displayer_appearances", view_name, appearance.id)


def get_appearance_object(view_name):
    ao = AppObjects()
    attributes = ao.design.findAttributes("displayer_appearances", view_name)

    appearance_object = defaultdict(list)

    if len(attributes) > 0:

        for attribute in attributes:
            item = attribute.parent

            if item is not None:
                appearance_object[attribute.value].append(item)

    return appearance_object


def build_appearances_from_object(view_name, appearance_object):

    for appearance_id, item_list in appearance_object.items():

        for item in item_list:
            item.attributes.add("displayer_appearances", view_name, appearance_id)


# Create a new custom view
class CaptureViewCommand(Fusion360CommandBase):

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()

        view_object = {"name": input_values['view_name_id']}

        custom_view_name = input_values["view_names_input"]

        if input_values["camera_input_checkbox"]:
            view_object["camera"] = build_camera_object()

        if input_values["display_input_checkbox"]:
            view_object["display_state"] = build_display_state_object()

        if input_values["visual_style_input_checkbox"]:
            view_object["visual_style"] = ao.app.activeViewport.visualStyle

        if input_values["appearances_input_checkbox"]:
            view_object["appearances"] = custom_view_name
            build_appearances(custom_view_name)

        if input_values["parameters_input_checkbox"]:
            view_object["parameters"] = build_parameter_object(True)

        json_string = json.dumps(view_object)

        ao.document.attributes.add('displayer_custom_views', custom_view_name, json_string)

        command_definition = ao.ui.commandDefinitions.itemById(
            'cmdID_SetViewCommand_' + custom_view_name[-1:]
        )
        command_definition.tooltip = input_values['view_name_id']
        command_definition.controlDefinition.isEnabled = True

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        ao = AppObjects()

        inputs.addStringValueInput('view_name_id', "View Name: ", "My Custom View")

        drop_input = inputs.addDropDownCommandInput("view_names_input", "Which View to save?",
                                                    adsk.core.DropDownStyles.TextListDropDownStyle)
        first = 0

        for custom_view_number in range(0, 10):
            view_name = "Custom View " + str(custom_view_number)
            view_def = ao.document.attributes.itemByName('displayer_custom_views', view_name)
            drop_input.listItems.add("Custom View " + str(custom_view_number), False)
            if view_def is None and first == 0:
                first = custom_view_number

        drop_input.listItems.item(first).isSelected = True

        inputs.addBoolValueInput("camera_input_checkbox", "Capture Camera?", True, '', True)
        inputs.addBoolValueInput("display_input_checkbox", "Capture Hide/Show State?", True, '', True)
        inputs.addBoolValueInput("visual_style_input_checkbox", "Capture Visual Style?", True, '', True)
        inputs.addBoolValueInput("appearances_input_checkbox", "Capture Appearances?", True, '', False)
        inputs.addBoolValueInput("parameters_input_checkbox", "Capture Parameters?", True, '', False)


# Set current view to a custom view
class SetViewCommand(Fusion360CommandBase):

    def __init__(self, cmd_def, debug):
        super().__init__(cmd_def, debug)

        self.custom_view_number = cmd_def.get('custom_view_number', None)

    # This is typically where your main program logic would go
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()

        view_name = "Custom View " + str(self.custom_view_number)
        view_def = ao.document.attributes.itemByName('displayer_custom_views', view_name)

        if view_def is not None:
            view_object = json.loads(view_def.value)
            camera_object = view_object.get("camera", None)
            display_state_object = view_object.get("display_state", None)
            visual_style = view_object.get("visual_style", None)
            appearances_view_name = view_object.get("appearances", None)
            parameters_object = view_object.get("parameters", None)

            if camera_object is not None:
                set_camera(camera_object)

            if display_state_object is not None:
                set_display_state(display_state_object)

            if visual_style is not None:
                ao.app.activeViewport.visualStyle = visual_style

            if appearances_view_name is not None:
                set_appearances(appearances_view_name)

            if parameters_object is not None:
                set_parameters(parameters_object)

    @staticmethod
    def get_tooltip(custom_view_number):
        ao = AppObjects()
        view_object_attribute = ao.document.attributes.itemByName(
            'displayer_custom_views',
            "Custom View " + str(custom_view_number)
        )
        if view_object_attribute is not None:
            tooltip = json.loads(view_object_attribute.value)["name"]
        else:
            tooltip = 'This View has not been set'

        return tooltip

    @staticmethod
    def get_view_exists(custom_view_number):
        ao = AppObjects()
        view_object_attribute = ao.document.attributes.itemByName(
            'displayer_custom_views',
            "Custom View " + str(custom_view_number)
        )
        if view_object_attribute is not None:
            exists = True
        else:
            exists = False

        return exists


# Manage the custom views in this model
class ManageViewsCommand(Fusion360CommandBase):

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        view_object_attributes = ao.document.attributes.itemsByGroup('displayer_custom_views')
        saved_views = {}

        appearance_views = {}

        for view_object_attribute in view_object_attributes:
            view_object = json.loads(view_object_attribute.value)
            saved_views[view_object["name"]] = view_object
            if view_object.get("appearances", None) is not None:
                appearance_views[view_object["name"]] = get_appearance_object(view_object["appearances"])
            else:
                appearance_views[view_object["name"]] = None
        delete_view_attributes()
        delete_tooltips()
        delete_appearance_attributes()

        for cmd_input in inputs:
            view_object = saved_views[cmd_input.name]
            appearance_object = appearance_views[cmd_input.name]
            view_name = cmd_input.selectedItem.name

            if not cmd_input.selectedItem.name == "**Delete This View**":
                ao.document.attributes.add('displayer_custom_views', view_name,
                                           json.dumps(view_object)
                                           )
                if appearance_object is not None:
                    build_appearances_from_object(view_name, appearance_object)

                command_defintion = ao.ui.commandDefinitions.itemById(
                    'cmdID_SetViewCommand_' + view_name[-1:]
                )

                command_defintion.tooltip = view_object["name"]
                command_defintion.controlDefinition.isEnabled = True

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        ao = AppObjects()

        view_object_attributes = ao.document.attributes.itemsByGroup('displayer_custom_views')

        if len(view_object_attributes) > 0:

            for view_object_attribute in view_object_attributes:
                view_object = json.loads(view_object_attribute.value)
                drop_input = inputs.addDropDownCommandInput("view_names_input_", view_object["name"],
                                                            adsk.core.DropDownStyles.TextListDropDownStyle)
                for custom_view_number in range(0, 10):
                    drop_input.listItems.add("Custom View " + str(custom_view_number), False)
                drop_input.listItems.item(int(view_object_attribute.name[-1:])).isSelected = True
                drop_input.listItems.add("**Delete This View**", False)
        else:
            ao.ui.messageBox("No views have been saved")


# Create a new custom view
class DeleteAllViewsCommand(Fusion360CommandBase):

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        delete_view_attributes()
        delete_tooltips()
        delete_appearance_attributes()

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        inputs.addTextBoxCommandInput("delete_text_input", "",
                                      "This will delete all saved views.  Are you sure you want to proceed?",
                                      5, True
                                      )


# Create a new custom view
class ExportAllViewsCommand(Fusion360CommandBase):

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()

        view_object_attributes = ao.document.attributes.itemsByGroup('displayer_custom_views')

        all_views = {}

        if view_object_attributes is not None:

            for view_object_attribute in view_object_attributes:
                view_object = json.loads(view_object_attribute.value)

        for custom_view_number in range(0, 10):
            view_object = get_view_from_number(custom_view_number)
            if view_object is not None:
                all_views["Custom View " + str(custom_view_number)] = view_object

        all_views_text = json.dumps(all_views)
        directory = input_values["export_dir_input"]

        if not os.path.exists(directory):
            os.makedirs(directory)

        file_name = os.path.join(directory, input_values["export_file_input"] + ".json")
        f = open(file_name, "w")
        f.write(all_views_text)
        f.close()

        settings = {
            "app_name": "Displayer",
            "default_dir": directory
        }

        write_settings("Displayer", settings)

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        ao = AppObjects()

        app_name = "Displayer"
        settings = read_settings(app_name)
        default_dir = settings.get("default_dir", get_default_dir(app_name))

        inputs.addStringValueInput("export_dir_input", "Directory Name", default_dir)

        default_name = ao.document.name
        inputs.addStringValueInput("export_file_input", "File Name", default_name)


# Create a new custom view
class ImportViewsCommand(Fusion360CommandBase):

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        app_name = "Displayer"

        settings = read_settings(app_name)

        # ao.ui.messageBox(str(settings))

        default_dir = settings.get("default_dir", get_default_dir(app_name))

        # ao.ui.messageBox(default_dir)

        file_dialog = ao.ui.createFileDialog()

        # file_dialog.initialDirectory = default_dir
        file_dialog.initialDirectory = "/Users/rainsbp/Dropbox/test_test_23"

        file_dialog.isMultiSelectEnabled = False

        file_dialog.title = 'Select a saved views file'
        file_dialog.filter = '*.*'

        # Show file open dialog
        dialog_result = file_dialog.showOpen()

        if dialog_result == adsk.core.DialogResults.DialogOK:
            file_name = file_dialog.filename
        else:
            return
        with open(file_name) as f:
            all_views = json.load(f)

        for view_name, view_object in all_views.items():
            ao.document.attributes.add('displayer_custom_views', view_name,
                                       json.dumps(view_object))

            command_defintion = ao.ui.commandDefinitions.itemById(
                'cmdID_SetViewCommand_' + view_name[-1:]
            )

            command_defintion.tooltip = view_object["name"]
            command_defintion.controlDefinition.isEnabled = True

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        inputs.addTextBoxCommandInput("import_text_input", "",
                                      "This will overwrite any current saved views with the same number "
                                      "as in the imported file.  \n\nAre you sure you want to proceed?",
                                      5, True
                                      )


class RefreshViewsCommand(Fusion360CommandBase):
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        refresh_custom_views()


class NormalToCommand(Fusion360CommandBase):
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()

        active_object = ao.design.activeEditObject

        # ao.ui.messageBox(active_object.name)
        # selections = ao.ui.activeSelections
        if active_object.objectType == adsk.fusion.Sketch.classType():

            selections = ao.ui.activeSelections
            # old_selections = selections.asArray()
            #
            selections.clear()
            # adsk.doEvents()
            selections.add(active_object)
            ao.ui.commandDefinitions.itemById("LookAtCommand").execute()
            ao.ui.commandDefinitions.itemById("cmdID_NormalToSketchCommand").execute()
            # ao.app.activeViewport.refresh()
            # ao.app.activeViewport.fit()
            # adsk.doEvents()
            # selections.clear()

        else:
            ao.ui.commandDefinitions.itemById("LookAtCommand").execute()

        # adsk.doEvents()
        # selections.clear()
            # ao.ui.terminateActiveCommand()

            # for old_selection in old_selections:
            #     if adsk.core.Base.cast(old_selection.entity) is not None:
            #         selections.add(old_selection.entity)
            # ao.ui.terminateActiveCommand()


class NormalToSketchCommand(Fusion360CommandBase):
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        ao.app.activeViewport.refresh()
        selections = ao.ui.activeSelections
        selections.clear()
        ao.app.activeViewport.fit()
        ao.ui.terminateActiveCommand()
        selections = ao.ui.activeSelections
        selections.clear()

