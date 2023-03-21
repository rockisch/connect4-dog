from dog.dog_interface import DogPlayerInterface

class PlayerInterface(DogPlayerInterface):
    def receive_start(self, start_status):
        raise NotImplementedError

    def receive_move(self, a_move):
        raise NotImplementedError

    def receive_withdrawal_notification(self):
        raise NotImplementedError
