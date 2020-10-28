
import datetime
import sqlalchemy as sa 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bottle import route,run,HTTPError,request

DB_PATH='sqlite:///albums.sqlite3'

Base=declarative_base()
class Album(Base):
	"""Описываем базу данных albums.sqlite3"""
	__tablename__ = "album"
	id = sa.Column(sa.INTEGER,primary_key=True)
	year = sa.Column(sa.INTEGER)
	artist = sa.Column(sa.TEXT)
	genre = sa.Column(sa.TEXT)
	album = sa.Column(sa.TEXT)


def connect_db():
	"""Функция подключения к базе данныхб возвращает сессию"""
	engine=sa.create_engine(DB_PATH)
	Base.metadata.create_all(engine)
	Session=sessionmaker(engine)
	
	return Session()


def find(artist):
	"""Функция находит артиста в базе данных и возвращает query-объект"""
	session=connect_db()
	albums=session.query(Album).filter(Album.artist==artist).all()
	return albums


@route("/albums/<artist>",method="GET")
def get_albums(artist):
	"""GET-запрос на поиск альбомов артиста"""
	list_albums=[]
	albums=find(artist)
	#Находим артиста в базе
	if  not albums:
		#Если не находим возвращаем ошибку 404
		mes="Артиста '{}' - не найдено".format(artist)
		message=HTTPError(404,mes)
	else:	
		#Если нашли артиста в базе данных формируем список альбомов
		for al in albums:
			list_albums.append(al.album)
			
		message="Альбомы имполнителя '{}', в количестве {} , найдены :".format(artist,len(list_albums))
		#Выводим список альбомов через запятую, на последнем ставим точку
		for al in list_albums:
			if al==list_albums[-1]:
				message+=str(al + ".")
			else:	
				
				message+=str(al + ",") 
	return message	


def save_album(album_obj):
	"""Функция принимает словарь с данными пользователя полученный из POST запросов
	и записывает его в базу данных"""
	session=connect_db()
	new_album=Album(year=album_obj['year'],artist=album_obj['artist'],genre=album_obj['genre'],album=album_obj['album'])
	session.add(new_album)
	session.commit()
	

def valid_data(album_obj):
	"""Функция проверяет валидность введеного пользователем года"""
	date_now=str(datetime.date.today()).split('-')
	#Получаем текущий год в date_now
	if len(album_obj['year'])!=4:
		#Проверяем длину года , должно быть 4 символа
		return False
	
	for digit in  album_obj['year'] :
		#Далее проверяем что введеный год состоит из цифр
		if digit not in  '0123456789':
			return False
	if int(album_obj['year']) <= int(date_now[0]):
		#И проверяем введеный пользователем год ,он должен быть не больше текущего года 
		return True
	else:
		return False		


def valid_artist(album_obj):
	"""Проверяем артиста и альбом на уникальность"""
	valid_artist=find(album_obj['artist'])
	#Находим артиста в БД по введеному артисту
	if not valid_artist:
		#Если его нет то возращаем TRUE
		return True
	else:
		for artist in valid_artist:
			#Если артист найден проходим по нему и сравниваем название альбомов
			if artist.album==album_obj['album']:
				return False

		return True			

@route("/albums",method="POST")	
def post_album():
	"""POST запрос на запись в БД"""
	album_obj={"artist":request.forms.get("artist"),"genre":request.forms.get("genre"),"year":request.forms.get("year"),"album":request.forms.get("album")}
	#Записыаем в словарь
	if not valid_data(album_obj):
		#Проверяем функцией проверки года
		message='Ошибка ввода года'
		result=HTTPError(406,message)
		return result


	if not valid_artist(album_obj):
		#Проверяем функцией проверки артиста и альбома
		message='Такой альбом этого артиста уже есть'
		result=HTTPError(409,message)
		return result
	else:
		save_album(album_obj)
		return "Данные успешно сохранены"

	


		




if __name__=="__main__":
	run(host="localhost",port=8080,debug=True)					











