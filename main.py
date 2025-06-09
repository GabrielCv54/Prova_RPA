import requests as r
import sqlite3 as sql
import sys 
import io
import re 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

def parte1_requisição():
    try:   
        url = 'https://api.adviceslip.com/advice'
        api = r.get(url)
        response = api.json()
        id = response['slip']['id']
        advice = response['slip']['advice']
        
        if api.status_code == 200:
            print(f'Um conselho pro seu dia 🚀')
            print(f'ID:{id}')
            print(f'Conselho: {advice}')
            return response
        else:
            print(f'Erro na requisição : {api.status_code}')
            return False
    except Exception as error:
        print(f'Erro : {error}')


def parte2_banco_de_dados(advice):
    try:
        id_advice = advice['slip']['id']
        advice_text = advice['slip']['advice']
        connection = sql.connect('projeto_rpa.db')
        cursor = connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dados_api(id INTEGER PRIMARY KEY ,conselho TEXT)
        ''')
        connection.commit()
            
        cursor.execute('''
        INSERT INTO dados_api(id,conselho) VALUES(?,?)
        ''',(id_advice,advice_text))
        connection.commit()
        connection.close()
    except sql.IntegrityError as e:
        print(f'Não é possível adicionar esse conselho, poís ele já existe, e o seu id não pode se repetir')

 
def parte3_processamento(response):
    '''Usei a biblioteca re para buscar vogais no texto do conselho e armazenar no banco de dados quais  e quantas vogais ele achou, da mesma forma as consoantes'''
    vogals_list = []
    consonants_list = []
    advice_text = response['slip']['advice']
    for letter in advice_text:
        vogals = re.compile(r'[aeiouAEIOU]')
        consonant = re.compile(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]')
        if vogals.search(letter):
         vogals_list.append(letter)
         vogals_string = ','.join(vogals_list)
        elif consonant.search(letter):
         consonants_list.append(letter)
         consonants_text = ','.join(consonants_list)
    print( {'Vogais':vogals_string,"QTTD_Vogais":len(vogals_list),'Consoantes':consonants_text,"Qttd_consoantes":len(consonants_list)})
    
    conn = sql.connect('projeto_rpa.db')
    cursor = conn.cursor()
    cursor.execute('''
  CREATE TABLE IF NOT EXISTS dados_processados(id INTEGER PRIMARY KEY AUTOINCREMENT,texto_base TEXT, vogais_encontradas TEXT,quantidade_vogais INTEGER, consoantes_encontradas TEXT,quantidade_consoantes INTEGER)
''')   

    cursor.execute('''
INSERT INTO dados_processados VALUES(?,?,?,?,?,?)
''',(response['slip']['id'],advice_text,vogals_string,len(vogals_list),consonants_text,len(consonants_list)))  
    conn.commit()
    conn.close()


def parte4_envio_de_email():
    try:    
        print('Aguarde pelo envio do email!!')
        server_email = smtplib.SMTP('smtp.gmail.com',port=587)
        server_email.starttls()
        server_email.login(user='gabriel.carvalhovieira123@gmail.com',password='uujl zmed qyfk onkt')

        sender = 'gabriel.carvalhovieira123@gmail.com'
        recipient = ['gabriel.carvalhovieira123@gmail.com','vanderson.bossi@faculdadeimpacta.com.br']
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = ", ".join(recipient)
        message['Subject'] = 'Texto de Email'

        body ='🔧 Esse projeto tem o intuito de testar os conhecimentos em : Requisição de API, armazemanento e manipulação dos dados dessa API em um banco de dados, utilizar a biblioteca re para expressões regulares , e como enviar email. Essa API que estou usando é uma API bem simples  sobre conselhos ,onde apenas possui campos de id e o conselho que sera mostrado ao usuário: \n {"slip": { "id": 86, "advice": "Never write in an email to someone, something which you wouldn`t say to that person`s face." "}}"'

        message.attach(MIMEText(body,'plain'))

        server_email.sendmail(sender,recipient,message.as_string())

        print('Email já enviado✅!!')
    except Exception as e:
        print(f'❌Algum erro ocorreu na criação do email❌\n Erro : {e}')


def main():
    '''response = parte1_requisição()
    database = parte2_banco_de_dados(response)
    process = parte3_processamento(response)'''
    email = parte4_envio_de_email()


if __name__ == '__main__':
    main()