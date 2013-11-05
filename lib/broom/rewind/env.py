import broom

class RewindEnv(broom.BroomObject):
    """Environment through which users can set cutoffs
    and other variables that affect all Rewind-related
    operations in a session.

    """
    @broom.field(broom.Settable)
    def AsOfTimeCutoff(self):
        return              # TODO: Now.

    @broom.field(broom.Settable)
    def _PhysicalTimeCutoff(self):
        return              # TODO: Now.

    def setAsOfDateCutoff(self, asOfDate):
        # TODO: Make a datetime object of
        #           asOfDate-23:59:59
        #       or more granular.
        asOfTime = None
        return [broom.NodeChange(broom.AsOfTimeCutoff, asOfTime)]

    @broom.field(delegate=setAsOfDateCutoff)
    def AsOfDateCutoff(self):
        # We just truncate to the last second/ms/ns of
        # the selected AsOfDate.
        return self.AsOfTimeCutoff().date()
