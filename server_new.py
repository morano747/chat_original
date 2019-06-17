from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor


class Client(Protocol):
    ip: str = None
    login: str = None
    factory: 'Chat'
    names = []

    def __init__(self, factory):
        """
        Инициализация фабрики клиента
        :param factory:
        """
        self.factory = factory

    def connectionMade(self):
        """
        Обработчик подключения нового клиента
        """
        self.ip = self.transport.getHost().host
        self.factory.clients.append(self)
        print(f"Client connected: {self.ip}")

        self.transport.write("Welcome to the chat v0.1\n".encode())

    def dataReceived(self, data: bytes):
        """
        Обработчик нового сообщения от клиента
        :param data:
        """
        message = data.decode().replace('\n', '')

        if self.login is not None:
            #print(self.login + "1") ###
            server_message = f"{self.login}: {message}"
            #print(server_message + "2")
            #print(message + "3")
            self.factory.notify_all_users(server_message)
           # print(self.factory.notify_all_users + "4")
           # print(self.factory.notify_all_users(server_message) + "5")
            self.factory.message.append(server_message)
           # print(self.factory.message + "6")
           # print(self.factory.message.append(server_message)+ "7")


            print(server_message)
        else: # так как без имени клиент не может писать в чат
            self.login = message.replace("login:", "")
            self.factory.clients_login.append(self.login)
            if 2 == self.factory.clients_login.count(self.login): # мы проверяем зарезервивано имя или нет
                self.transport.write(f"login: '{self.login}' is reserved\n".encode())
                self.transport.write(f"Your login >>> ".encode()) #усли да, то повторно просим ввести логин
                self.factory.clients_login.remove(self.login)
                self.login = None # и обнуляем логин, чтобы следующий ответ был присвоен как имя
            else: #если нет, то добро пожаловать
                notification = f"New user connected: {self.login}"
                self.factory.message.append(notification)  # добавляет в список пользователей
                self.factory.notify_all_users(notification, self)

                self.transport.write("Welcome to the chat v0.1".encode())

                self.transport.write("old messages:\n".encode())
                for send in range(0, len(self.factory.message) -1 ):
                    self.transport.write(f"{send +1}: {self.factory.message[send]}\n".encode())
                print(notification)


    def connectionLost(self, reason=None):
        """
        Обработчик отключения клиента
        :param reason:
        """
        self.factory.clients.remove(self)
        print(f"Client disconnected: {self.ip}")



class Chat(Factory):
    clients: list

    def __init__(self):
        """
        Инициализация сервера
        """
        self.clients = []
        print("*" * 10, "\nStart server \nCompleted [OK]")

    def startFactory(self):
        """
        Запуск процесса ожидания новых клиентов
        :return:
        """
        print("\n\nStart listening for the clients...")

    def buildProtocol(self, addr):
        """
        Инициализация нового клиента
        :param addr:
        :return:
        """
        return Client(self)

    def notify_all_users(self, data: str):
        """
        Отправка сообщений всем текущим пользователям
        :param data:
        :return:
        """
        for user in self.clients:
            user.transport.write(f"{data}\n".encode())


if __name__ == '__main__':
    reactor.listenTCP(7410, Chat())
    reactor.run()
