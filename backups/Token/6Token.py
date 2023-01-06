BackupTime = 'Fri Jan  6 00:24:01 2023'#Automatically generated backup time
import os
import time
import random
import hashlib


class TokenStore:
    """
	A class to handle tokens (Not encrypted)
	"""

    def __init__(self, filename, token_length=10, token_time=30):
        self.name = filename  # Filename for token store
        self.token_time = token_time  # Valid token time (in minutes)
        self.tl = token_length  # Length of tokens in characters
        self.data = {}
        if not os.path.exists(self.name):
            with open(self.name, "w") as e:
                e.write("{}")

    def _timestamp(self):
        """
		Returns a tuple that includes the time information needed for tokens.
		"""
        cur = time.gmtime()
        form = (cur.tm_yday, cur.tm_min, cur.tm_hour)
        return form

    def generate_token(self):
        """
		Generates a token, registers it, and returns it.
		"""
        token_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890=+-_()*!@#.><[]{}|"
        token = ""
        for i in range(self.tl):
            token += random.choice(token_chars)
        self.write(token)
        return token

    def remove_token(self, token):
        """
		Tries to remove a token
		"""
        try:
            self.data.pop(hashlib.md5(token.encode()).hexdigest())
            self.save()
            return True
        except:
            return False

    def save(self):
        """
		Write the data to the save file
		"""
        with open(self.name, "w") as e:
            e.write(str(self.data))

    def write(self, token):
        """
		Register the token and write data to save file
		"""
        token = hashlib.md5(token.encode()).hexdigest()# Encrypt token for storage
        token = str(token).replace("b'","")#GEt rid of bytes identifier
        token = token.replace("'","")
        self.data[f'{token}'] = self._timestamp()
        self.save()

    def check(self, token):
        """
		Checks if a token has expired. True if the token is valid, False if not.
		"""
        token = hashlib.md5(token.encode()).hexdigest()# Encrypt token for comparing
        token = str(token).replace("b'","")# Get rid of bytes identifier
        token = token.replace("'","")
        cur = self._timestamp()
        result = True
        if token in self.data:
            if self.data[token][0] != cur[0]:
                result = False
            elif self.data[token][2] != cur[2]:
                result = False
            elif cur[1] >= self.data[token][1] + self.token_time:
                result = False
        else:
            result = False
        return result

    def read(self):
        """
		Read the savefile data.
		"""
        with open(self.name, "r") as e:
            try:
                b = eval(e.read())
            except:
                b = {}
        self.data = b
