from qualityAssurance.checks import getChecks
import pyblish
import pyblish.api
import pyblish.util

import logging
log = logging.getLogger("pyblish.plugin")

# qualityAssurance state levels
SUCCESS = 0
WARNING = 1
ERROR = 2

# if you register plugin path this wont be picked up
# this class adds support for this
# note the registering should happen during pickup of plugin
# atm it happens during processing. this is inconvienent because it
# requires the user to refresh the GUI for the plugins to show
# todo implement proper support for path registering (if pyblish allows this)
# for now it's preferable to use setup()
class CollectQualityAssuranceWrapperPlugin(pyblish.api.Collector):
    """
    create wrapper plugins for quality assurance checks
    this plugin is only needed if you rely on pyblish's register path
    you can also trigger a manual setup with the setup function in this module.
    """
    # plugin attributes
    families = ['*']
    hosts = ['maya']
    label = 'collect QualityAssurance wrappers'
    optional = True

    def process(self):
        setup()


def setup():
    """
    register all checks from qualityAssurance as pyblish plugins.
    every check will be setup as a context plugin that checks the whole scene.
    it won't run on specific instances, due to the way the qualityAssurance.checks are coded
    """
    for wrapper_plugin in all_checks_to_plugins_iter():
        pyblish.api.register_plugin(wrapper_plugin)


def all_checks_to_plugins_iter():
    for check in getChecks():
        wrapper_plugin = create_plugin_from_check(check)
        yield wrapper_plugin


def create_plugin_from_check(check):
    """
    check: the check we want to convert to a pyblish plugin, type: qualityAssurance.checks.QualityAssurance
    returns a Pyblish plugin class, wrapped around the check.
    """
    check_type = type(check)

    # hide non fixable actions
    actions_value = []
    if check.isFixable():
        actions_value.append(ActionFix)

    # hide non selectable actions
    if check.isSelectable():
        actions_value.append(ActionSelect)

    class QualityAssuranceWrapperPlugin(pyblish.api.Validator):
        # plugin attributes
        families = check._categories
        hosts = ['maya']
        label = 'Scene: ' + check._name
        optional = True
        __doc__ = check.__doc__
        actions = actions_value
        check_class = check_type

        def process(self, context):
            self.check = self.check_class()
            context.data[self.label] = self
            if self.check.isFindable():
                self.check.find()

                if self.check.state == ERROR:
                    raise Exception(self.check._message)
                    # assert not self.check.errors, self._check_error_msg

                if self.check.state == WARNING:
                    log.warning(self.check._message)


    QualityAssuranceWrapperPlugin.__name__ = 'Validate' + check.__class__.__name__ + 'PyblishWrapper'
    return QualityAssuranceWrapperPlugin


class ActionFix(pyblish.api.Action):
    label = "Fix"
    on = "failedOrWarning"
    icon = "hand-o-up"  # Icon from Awesome Icon

    def process(self, context, plugin):
        # get used plugin instance
        plugin_inst = context.data[plugin.label]
        check = plugin_inst.check

        if not check.isFixable():
            log.warning('fix is not supported for this check:' + check._name)
            return

        check.fix()
        assert check.state == SUCCESS, 'failed to fix.'
        log.info('fixing: ' + plugin.label)
        # todo after the fix ideally we also update pyblish plugin to set state to green?


class ActionSelect(pyblish.api.Action):
    label = "select failed nodes"
    on = "failedOrWarning"
    icon = "hand-o-up"  # Icon from Awesome Icon

    def process(self, context, plugin):
        # get used plugin instance
        plugin_inst = context.data[plugin.label]
        check = plugin_inst.check

        if not check.isSelectable():
            log.warning('select is not supported for this check:' + check._name)
            return

        check.select()
        log.info('selecting: ' + str(check.errors))


