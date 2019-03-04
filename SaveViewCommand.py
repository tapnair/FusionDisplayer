import adsk.core
import adsk.fusion
import traceback

from .Fusion360Utilities.Fusion360Utilities import AppObjects, get_default_dir
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase

import json


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


def set_view(view_object):
    ao = AppObjects()

    camera = ao.app.activeViewport.camera

    camera.cameraType = view_object["camera_type"]
    camera.eye = get_point(view_object["eye"])
    camera.isFitView = view_object["is_fit_view"]
    camera.isSmoothTransition = view_object["is_smooth"]
    camera.target = get_point(view_object["target"])
    camera.upVector = get_vector(view_object["up_vector"])
    camera.viewExtents = view_object["view_extents"]
    camera.viewOrientation = view_object["view_orientation"]

    if not view_object["camera_type"] == adsk.core.CameraTypes.OrthographicCameraType:
        camera.perspectiveAngle = view_object["perspective_angle"]

    ao.app.activeViewport.visualStyle = view_object["visual_style"]
    ao.app.activeViewport.camera = camera


def build_view_object(name):
    ao = AppObjects()
    camera = ao.app.activeViewport.camera

    view_object = {
        "name": name,

        "visual_style": ao.app.activeViewport.visualStyle,
        "camera_type": camera.cameraType,
        "eye": make_point(camera.eye),
        "is_fit_view": camera.isFitView,
        "is_smooth": camera.isSmoothTransition,
        "target": make_point(camera.target),
        "up_vector": make_vector(camera.upVector),
        "view_extents": camera.viewExtents,
        "view_orientation": camera.viewOrientation
    }
    if not view_object["camera_type"] == adsk.core.CameraTypes.OrthographicCameraType:
        view_object["perspective_angle"] = camera.perspectiveAngle

    return view_object


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


# Create a new custom view
class CaptureViewCommand(Fusion360CommandBase):

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()

        view_object = build_view_object(input_values['view_name_id'])

        json_string = json.dumps(view_object)

        ao.document.attributes.add('displayer_custom_views', input_values["view_names_input"], json_string)

        command_defintion = ao.ui.commandDefinitions.itemById(
            'cmdID_SetViewCommand_' + input_values["view_names_input"][-1:]
        )
        command_defintion.tooltip = input_values['view_name_id']
        command_defintion.controlDefinition.isEnabled = True

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        inputs.addStringValueInput('view_name_id', "View Name: ", "My Custom View")

        drop_input = inputs.addDropDownCommandInput("view_names_input", "Which View to save?",
                                                    adsk.core.DropDownStyles.TextListDropDownStyle)
        for custom_view_number in range(0, 10):
            drop_input.listItems.add("Custom View " + str(custom_view_number), False)
        drop_input.listItems.item(0).isSelected = True


# Set current view to a custom view
class SetViewCommand(Fusion360CommandBase):

    def __init__(self, cmd_def, debug):
        super().__init__(cmd_def, debug)

        self.custom_view_number = cmd_def.get('custom_view_number', None)

    # This is typically where your main program logic would go
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()

        view_def = ao.document.attributes.itemByName(
            'displayer_custom_views',
            "Custom View " + str(self.custom_view_number)
        )

        if view_def is not None:
            view_object = json.loads(view_def.value)
            set_view(view_object)

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

        for view_object_attribute in view_object_attributes:
            view_object = json.loads(view_object_attribute.value)
            saved_views[view_object["name"]] = view_object

        delete_view_attributes()
        delete_tooltips()

        for cmd_input in inputs:
            view_object = saved_views[cmd_input.name]

            if not cmd_input.selectedItem.name == "**Delete This View**":
                ao.document.attributes.add('displayer_custom_views', cmd_input.selectedItem.name,
                                           json.dumps(view_object))

                command_defintion = ao.ui.commandDefinitions.itemById(
                    'cmdID_SetViewCommand_' + cmd_input.selectedItem.name[-1:]
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
        file_name = input_values["export_dir_input"] + input_values["export_file_input"] + ".json"
        f = open(file_name, "w")
        f.write(all_views_text)
        f.close()


    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        default_dir = get_default_dir("Displayer")
        inputs.addStringValueInput("export_dir_input", "Directory Name", default_dir)

        inputs.addStringValueInput("export_file_input", "File Name", "Displayer_saved_views")


# Create a new custom view
class ImportViewsCommand(Fusion360CommandBase):

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        default_dir = get_default_dir("Displayer")

        file_dialog = ao.ui.createFileDialog()

        file_dialog.initialDirectory = default_dir

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