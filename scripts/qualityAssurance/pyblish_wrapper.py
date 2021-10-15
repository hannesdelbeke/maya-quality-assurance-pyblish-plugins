from qualityAssurance.checks import getChecks
import pyblish
import pyblish.api
import pyblish.util


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
    class QualityAssuranceWrapperPlugin(pyblish.api.Validator):
        # plugin attributes
        families = check._categories
        hosts = ['maya']
        label = 'Scene: ' + check._name
        optional = True
        __doc__ = check.__doc__

        check_class = check_type

        # check attributes
        _check_error_msg = check._message
        _check_findable = check.isFindable()
        _check_find = check.find

        def process(self, context):
            check = self.check_class()
            if self._check_findable:
                check.find()
                # self._check_find()
                print(check.errors)
                assert not check.errors, self._check_error_msg
            # self.log.info("Publishing to studio library.")

    QualityAssuranceWrapperPlugin.__name__ = 'Validate' + check.__class__.__name__ + 'PyblishWrapper'
    return QualityAssuranceWrapperPlugin
