class CartInvoker:
    def __init__(self):
        self.command_history = []  
    
    def execute_command(self, command):
        self.command_history.append(command)
        command.execute()
    
    def undo_last_command(self):
        if self.command_history:
            last_command = self.command_history.pop()
            last_command.undo() 