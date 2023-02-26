class GuestBook:
    def __init__(self) -> None:
        self.id = None
        self.username = None
        self.comment = None
        self.posted_on = None

    def __str__(self) -> str:
        return "id=" + str(self.id) + "; username=" + self.username + "; comment=" + self.comment + "; posted_on=" + str(self.posted_on)