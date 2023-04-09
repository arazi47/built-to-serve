class GuestBook:
    def __init__(self, id=None, username=None, comment=None, posted_on=None) -> None:
        self.id = id
        self.username = username
        self.comment = comment
        self.posted_on = posted_on

    def __str__(self) -> str:
        return "id=" + str(self.id) + "; username=" + str(self.username) + "; comment=" + str(self.comment) + "; posted_on=" + str(self.posted_on)