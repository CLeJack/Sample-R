from sample_r.bus import bus, MessageType, UIMessage

class BaseComponent:
    def __init__(self, cid: str, mtype: MessageType):
        self.cid = cid
        self.mtype = mtype

    def emit(self, value: any = None):
        """Pushes a message out to the app."""
        bus.push(self.mtype, self.cid, value)

    def respond(self, msg: UIMessage):
        """
        Logic to run when the component receives a message from the bus.
        To be overridden by child classes.
        """
        pass