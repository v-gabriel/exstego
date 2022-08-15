import os
from termcolor import colored


class MessageHelper:
    is_colored_logger = False

    to_print = True

    full_log = ""
    src = ""
    __identifier = "MessageHelper"

    @classmethod
    def error(cls, message, identifier='', error=''):
        color = 'red'
        plain_title = '[Error]'
        title = colored(plain_title, color, attrs=['reverse', 'blink'])
        if identifier != '':
            identifier = f"[{identifier}]\n"
        if error != '':
            error = f"\n@error:\n{str(error)}"
        plain_text = f"{identifier}{message}{error}"
        text = colored(plain_text, color)

        plain_log = f"#{plain_title}#\n{plain_text}\n\n"
        log = f'{title}\n{text}\n'
        cls.full_log += plain_log

        if cls.to_print:
            if cls.is_colored_logger:
                print(log)
            else:
                print(plain_log)

    @classmethod
    def warning(cls, message, identifier=''):
        color = 'yellow'
        plain_title = '[Warning]'
        title = colored(plain_title, color, attrs=['reverse', 'blink'])
        if identifier != '':
            identifier = f"[{identifier}]\n"
        plain_text = f"{identifier}{message}"
        text = colored(plain_text, color)

        plain_log = f"#{plain_title}#\n{plain_text}\n\n"
        log = f'{title}\n{text}\n'
        cls.full_log += plain_log

        if cls.to_print:
            if cls.is_colored_logger:
                print(log)
            else:
                print(plain_log)

    @classmethod
    def success(cls, message, identifier=''):
        color = 'green'
        plain_title = '[Success]'
        title = colored(plain_title, color, attrs=['reverse', 'blink'])
        if identifier != '':
            identifier = f"[{identifier}]\n"
        plain_text = f"{identifier}{message}"
        text = colored(plain_text, color)

        plain_log = f"#{plain_title}#\n{plain_text}\n\n"
        log = f'{title}\n{text}\n'
        cls.full_log += plain_log

        if cls.to_print:
            if cls.is_colored_logger:
                print(log)
            else:
                print(plain_log)

    @classmethod
    def log(cls, message, identifier=''):
        color = 'blue'
        plain_title = '[Log]'
        title = colored(plain_title, color, attrs=['reverse', 'blink'])
        if identifier != '':
            identifier = f"[{identifier}]\n"
        plain_text = f"{identifier}{message}"
        text = colored(plain_text, color)

        plain_log = f"#{plain_title}#\n{plain_text}\n\n"
        log = f'{title}\n{text}\n'
        cls.full_log += plain_log

        if cls.to_print:
            if cls.is_colored_logger:
                print(log)
            else:
                print(plain_log)

    @classmethod
    def save_logs(cls):
        try:
            if cls.src and cls.src != '':
                destination = cls.src
                filename = '/logs.txt'
                os.makedirs(destination, exist_ok=True)

                text_file = open(destination + filename, "w", encoding="utf-8")
                n = text_file.write(cls.full_log)
                text_file.close()
            else:
                raise Exception("Invalid folder.")
        except Exception as exception:
            MessageHelper.error("Error while saving logs.", cls.__identifier, exception)
