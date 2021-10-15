# maya-quality-assurance pyblish port
Convert checks from the repo maya-quality-assurance to pyblish plugins.
The original repo can be found on [Git](https://github.com/robertjoosten/maya-quality-assurance)

# setup
- /scripts/ needs to be added to the path
- you need pyblish ofcourse
- register the plugins with command:

# develop guide
I try to leave original files untouched to make any future merges easy.

pyblish validation plugins setup example
```
class ValidateExportPath(pyblish.api.Validator):
    """check some animation things"""
    label = "animation validation"
    hosts = ['maya']
    families = ['animation']
    optional = True
    actions = [my_action, ...]
    active = False

    def process(self, instance):
	    pass
```

maya-quality-assurance example:
```
class NotConnectedAnimation(QualityAssurance):
    """
    Animation curves will be checked to see if the output value is connected.
    When fixing this error the non-connected animation curves will be deleted.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Unused Animation"
        self._message = "{0} animation curve(s) are unused"
        self._categories = ["Animation"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Animation curves without output connection
        :rtype: generator
        """
        animCurves = self.ls(type="animCurve")
        animCurves = reference.removeReferenced(animCurves)

        for animCurve in animCurves:
            # check if the output plug is connected
            if cmds.listConnections("{0}.output".format(animCurve)):
                continue

            # yield error
            yield animCurve

    def _fix(self, animCurve):
        """
        :param str animCurve:
        """
        cmds.delete(animCurve)
```

all we need to do is hookup
- QualityAssurance._find -------> plugin.process
- QualityAssurance._fix --------> action
- QualityAssurance.__doc__ -----> plugin.__doc__
- QualityAssurance._name -------> plugin.label
- QualityAssurance._message ----> the assert message
- QualityAssurance._categories -> plugin.families

- QualityAssurance._selectable, list if errorlist is selectable, might hookup to a select action
- QualityAssurance._urgency 1=orange, 2=red, can be hooked up to warning/error
	
Note that QualityAssurance requires an instance, whereas plugin stores this info in the class vars.
	
- see [pyblish docs](https://api.pyblish.com/pyblish.util/util.validate)
- see [maya quality-assurance docs](docs/qualityAssurance.html)