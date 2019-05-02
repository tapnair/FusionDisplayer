# Importing sample Fusion Command
# Could import multiple Command definitions here
from .Demo1Command import Demo1Command
from .SaveViewCommand import SetViewCommand, CaptureViewCommand, ManageViewsCommand, \
    DeleteAllViewsCommand, ImportViewsCommand, ExportAllViewsCommand, RefreshViewsCommand, \
    NormalToCommand, NormalToSketchCommand
from .DemoPaletteCommand import DemoPaletteShowCommand, DemoPaletteSendCommand

commands = []
command_definitions = []

command_in_nav_bar = False
workspaces = ['FusionSolidEnvironment', "CAMEnvironment"]
panel = 'Displayer'

# Define parameters for 1st command
cmd = {
    'cmd_name': 'Save View',
    'cmd_description': 'Save The Current Viewport',
    'cmd_id': 'cmdID_CaptureViewCommand',
    'cmd_resources': './resources',
    'workspace': workspaces,
    'toolbar_panel_id': panel,
    'command_promoted': True,
    'command_in_nav_bar': command_in_nav_bar,
    'class': CaptureViewCommand
}
command_definitions.append(cmd)

# Define parameters for 1st command
cmd = {
    'cmd_name': 'Manage Views',
    'cmd_description': 'Manage your saved views',
    'cmd_id': 'cmdID_ManageViewsCommand',
    'cmd_resources': './resources',
    'workspace': workspaces,
    'toolbar_panel_id': panel,
    'command_promoted': False,
    'command_in_nav_bar': command_in_nav_bar,
    'class': ManageViewsCommand
}
command_definitions.append(cmd)

# Define parameters for 1st command
cmd = {
    'cmd_name': 'Refresh Views',
    'cmd_description': 'Refresh your saved views list',
    'cmd_id': 'cmdID_RefreshViewsCommand',
    'cmd_resources': './resources',
    'workspace': workspaces,
    'toolbar_panel_id': panel,
    'add_to_drop_down': True,
    'drop_down_cmd_id': 'cmd_id_saved_views',
    'drop_down_resources': './resources',
    'drop_down_name': "Saved Views",
    'command_promoted': False,
    'command_in_nav_bar': command_in_nav_bar,
    'class': RefreshViewsCommand
}
command_definitions.append(cmd)

for view_number in range(0, 10):
    # Define parameters for 2nd command
    cmd = {
        'cmd_name': 'Custom View ' + str(view_number),
        'cmd_description': SetViewCommand.get_tooltip(view_number),
        'cmd_id': 'cmdID_SetViewCommand_' + str(view_number),
        'cmd_resources': './resources',
        'workspace': workspaces,
        'toolbar_panel_id': panel,
        'custom_view_number': view_number,
        'command_enabled': SetViewCommand.get_view_exists(view_number),
        'add_to_drop_down': True,
        'drop_down_cmd_id': 'cmd_id_saved_views',
        'drop_down_resources': './resources',
        'drop_down_name': "Saved Views",
        'command_in_nav_bar': command_in_nav_bar,
        'class': SetViewCommand
    }
    command_definitions.append(cmd)

# Define parameters for 1st command
cmd = {
    'cmd_name': 'Delete All Custom Views',
    'cmd_description': 'This cannot be undone',
    'cmd_id': 'cmdID_DeleteAllViewsCommand',
    'cmd_resources': './resources',
    'workspace': workspaces,
    'toolbar_panel_id': panel,
    'command_promoted': False,
    'command_in_nav_bar': command_in_nav_bar,
    'class': DeleteAllViewsCommand
}
command_definitions.append(cmd)

# Define parameters for 1st command
cmd = {
    'cmd_name': 'Import Custom Views',
    'cmd_description': 'This cannot be undone',
    'cmd_id': 'cmdID_ImportViewsCommand',
    'cmd_resources': './resources',
    'workspace': workspaces,
    'toolbar_panel_id': panel,
    'command_promoted': False,
    'command_in_nav_bar': command_in_nav_bar,
    'class': ImportViewsCommand
}
command_definitions.append(cmd)

# Define parameters for 1st command
cmd = {
    'cmd_name': 'Export All Custom Views',
    'cmd_description': 'Save all the view definitions',
    'cmd_id': 'cmdID_ExportAllViewsCommand',
    'cmd_resources': './resources',
    'workspace': workspaces,
    'toolbar_panel_id': panel,
    'command_promoted': False,
    'command_in_nav_bar': command_in_nav_bar,
    'class': ExportAllViewsCommand
}
command_definitions.append(cmd)


# Define parameters for 1st command
cmd = {
    'cmd_name': 'Normal To',
    'cmd_description': 'Look At, with enhancements',
    'cmd_id': 'cmdID_NormalToCommand',
    'cmd_resources': './resources',
    'workspace': workspaces,
    'toolbar_panel_id': panel,
    'command_promoted': False,
    'command_in_nav_bar': command_in_nav_bar,
    'class': NormalToCommand
}
command_definitions.append(cmd)

# Define parameters for 1st command
cmd = {
    'cmd_name': 'Normal To',
    'cmd_description': 'Look At, with enhancements',
    'cmd_id': 'cmdID_NormalToSketchCommand',
    'cmd_resources': './resources',
    'workspace': workspaces,
    'toolbar_panel_id': panel,
    'command_promoted': False,
    'command_visible': False,
    'command_in_nav_bar': command_in_nav_bar,
    'class': NormalToSketchCommand
}
command_definitions.append(cmd)

# # Define parameters for 2nd command
# cmd = {
#     'cmd_name': 'Fusion Palette Demo Command',
#     'cmd_description': 'Fusion Demo Palette Description',
#     'cmd_id': 'cmdID_palette_demo_1',
#     'cmd_resources': './resources',
#     'workspace': workspaces,
#     'toolbar_panel_id': 'SolidScriptsAddinsPanel',
#     'command_visible': True,
#     'command_promoted': False,
#     'palette_id': 'demo_palette_id',
#     'palette_name': 'Demo Palette Name',
#     'palette_html_file_url': 'demo.html',
#     'palette_is_visible': True,
#     'palette_show_close_button': True,
#     'palette_is_resizable': True,
#     'palette_width': 500,
#     'palette_height': 600,
#     'class': DemoPaletteShowCommand
# }
# command_definitions.append(cmd)
#
# # Define parameters for 2nd command
# cmd = {
#     'cmd_name': 'Fusion Palette Send Command',
#     'cmd_description': 'Send info to Fusion 360 Palette',
#     'cmd_id': 'cmdID_palette_send_demo_1',
#     'cmd_resources': './resources',
#     'workspace': workspaces,
#     'toolbar_panel_id': 'SolidScriptsAddinsPanel',
#     'command_visible': True,
#     'command_promoted': False,
#     'palette_id': 'demo_palette_id',
#     'class': DemoPaletteSendCommand
# }
# command_definitions.append(cmd)

# Set to True to display various useful messages when debugging your app
debug = False


# Don't change anything below here:
for cmd_def in command_definitions:
    command = cmd_def['class'](cmd_def, debug)
    commands.append(command)


def run(context):

    for run_command in commands:
        run_command.on_run()


def stop(context):
    for stop_command in commands:
        stop_command.on_stop()
