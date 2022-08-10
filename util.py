import imp
import string,random
from transliterate import translit

characters = list(string.ascii_letters + string.digits)

def generate_random_password(length: int):
	## shuffling the characters
	random.shuffle(characters)
	
	## picking random characters from the list
	password = []
	for i in range(length):
		password.append(random.choice(characters))

	## shuffling the resultant password
	random.shuffle(password)

	## converting the list to string
	## printing the list
	return "".join(password)

def renamer(name):
	name = name.replace(' ','_')
	name = name.replace('/','x').replace('\'','x').replace('"','x').replace('!','x').replace('@','x').replace('#','x').replace('№','x').replace(';','x').replace('$','x').replace('%','x').replace('^','x').replace('&','x').replace('?','x').replace('.','x').replace(',','x').replace('*','x').replace('(','x').replace(')','x').replace('-','x').replace('=','x').replace('+','x').replace('>','x').replace('<','x').replace('[','x').replace(']','x').replace('{','x').replace('}','x').replace(':','x')
	return translit(name, reversed=True)