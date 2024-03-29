import discord
import os
import pymysql.cursors
import keep_alive


keep_alive.keep_alive()
settings = {'token': os.getenv("TOKEN"), 'id': os.getenv("ID")}
text_last = []


def getConnection():
    tries = 0
    while tries < 2:
        tries += 1
        try:
            connection = pymysql.connect(
                host=os.getenv("HOST"),
                user=os.getenv("USER"),
                password=os.getenv("PASSWORD"),
                db=os.getenv("DB"),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            return connection
        except:
            print("ERROR during connecting to MySQL...reconnecting, tries = ", tries)
    return None

def getConnection2():
    tries = 0
    while tries < 2:
        tries += 1
        try:
            connection = pymysql.connect(
                host=os.getenv("HOST2"),
                user=os.getenv("USER2"),
                password=os.getenv("PASSWORD2"),
                db=os.getenv("DB2"),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            return connection
        except Exception as e:
            print("ERROR2 during connecting to MySQL...reconnecting, tries = ", tries)
            print(e)
    return None

def make_order(text, id):
    text = text[text.find(':') + 2:]
    text = text.split(', ')
    product = text[0]
    shop_name = text[1]
    amount = text[2]
    balance = 0
    batch = 0
    connection2 = getConnection2()
    connection = getConnection()
    with connection.cursor() as cursor:
                sql = "SELECT batch FROM Products WHERE product = %s"
                cursor.execute(sql, shop_name)
                rows = cursor.fetchall()
                for row in rows:
                    batch = row['batch']
    if amount % batch == 0:
        pass
    else: 
        return 0
    try:
        with connection.cursor() as cursor:
                sql = "SELECT id FROM Shops WHERE name = %s"
                cursor.execute(sql, shop_name)
                rows = cursor.fetchall()
                for row in rows:
                    shop_id = row['id']
        with connection.cursor() as cursor:
                sql = "SELECT price FROM Products WHERE id_shop = %s"
                cursor.execute(sql, shop_id)
                rows = cursor.fetchall()
                for row in rows:
                    price = row['price']
        total_price = int(price) * int(amount)
        with connection2.cursor() as cursor:
                sql = "SELECT balance FROM kbank_accounts WHERE discord = %s"
                cursor.execute(sql, id)
                rows = cursor.fetchall()
                for row in rows:
                    balance = row['balance']
    except:
        return 0
    if balance < total_price:
        return 0
    else:
        return_to = []
        return_to.append(amount)
        return_to.append(product)
        return_to.append(total_price)
        return_to.append(shop_id)
        return return_to

def confirm_order(array):
    array2 = [array]
    amount = int(array[0])
    product = str(array[1])
    total_price = int(array[2])
    user_id = int(array[4])
    shop_id = int(array[3])
    tozon_id = "830123622143230004"
    owner_id = ''
    connection = getConnection()
    connection2 = getConnection2()
    try:
        with connection2.cursor() as cursor:
            sql = "UPDATE kbank_accounts SET balance = balance - %s WHERE discord = %s"
            cursor.execute(sql, (total_price, user_id))
            connection2.commit()
        with connection2.cursor() as cursor:
            sql = "UPDATE kbank_accounts SET balance = balance + %s WHERE discord = %s"
            cursor.execute(sql, (total_price, tozon_id))
            connection2.commit()
        with connection.cursor() as cursor:
            sql = "SELECT owner_id FROM Shops WHERE id = %s"
            cursor.execute(sql, shop_id)
            rows = cursor.fetchall()
            for row in rows:
                owner_id = row['owner_id']
        array2.append(remove_good(product, owner_id, amount))
        with connection.cursor() as cursor:
                cursor.execute('INSERT INTO Orders VALUES(%s,%s,%s,%s,%s,%s)',(0, user_id, product, amount, total_price, shop_id))
                connection.commit()
        with connection.cursor() as cursor:
            sql = "SELECT owner_id FROM Shops WHERE id = %s"
            cursor.execute(sql, shop_id)
            rows = cursor.fetchall()
            for row in rows:
                id = row['owner_id']
            array.append(int(id))
        return array2
    except Exception:
        return 0
    
def get_order(id, product):
    connection = getConnection()
    connection2 = getConnection2()
    tozon_id = "830123622143230004"
    id_shop = 0
    summ = 0 
    owner_id = 0
    try:
        with connection.cursor() as cursor:
            sql = "SELECT shop_id FROM Orders WHERE customer_id = %s"
            cursor.execute(sql, id)
            rows = cursor.fetchall()
            for row in rows:
                id_shop = int(row['shop_id'])
        with connection.cursor() as cursor:
            sql = "SELECT owner_id FROM Shops WHERE id = %s"
            cursor.execute(sql, id_shop)
            rows = cursor.fetchall()
            for row in rows:
                owner_id = int(row['owner_id'])
        with connection.cursor() as cursor:
            sql = "SELECT total_price FROM Orders WHERE customer_id = %s"
            cursor.execute(sql, id)
            rows = cursor.fetchall()
            for row in rows:
                summ = int(row['total_price'])
        with connection.cursor() as cursor:
            sql = "DELETE FROM Orders WHERE customer_id = %s AND product = %s"
            cursor.execute(sql, (str(id), str(product)))
            connection.commit()
        with connection2.cursor() as cursor:
            sql = "UPDATE kbank_accounts SET balance = balance - %s WHERE discord = %s"
            cursor.execute(sql, (int(summ), str(tozon_id)))
            connection2.commit()

        with connection2.cursor() as cursor:
            sql = "UPDATE kbank_accounts SET balance = balance + %s WHERE discord = %s"
            cursor.execute(sql, (int(summ), str(owner_id)))
            connection2.commit()  
        return owner_id
    except:
        return 0
    

def create_shop(name, owners_id):
    connection = getConnection()
    balance = 0
    connection2 = getConnection2()
    try:
        with connection2.cursor() as cursor:
                sql = "SELECT balance FROM kbank_accounts WHERE discord = %s"
                cursor.execute(sql, id)
                rows = cursor.fetchall()
                for row in rows:
                    balance = int(row['id'])
    except:
        return 0
    try:
        with connection.cursor() as cursor:
                cursor.execute('INSERT INTO Shops VALUES(%s,%s,%s)',(0, name, str(owners_id)))
                connection.commit()
        return 1
    except Exception:
        return 0

def add_goods(name, price, id, amount, batch):
        id_shop = 0
        nam = ''
        connection = getConnection()
        try:
            with connection.cursor() as cursor:
                    sql = "SELECT id FROM Shops WHERE owner_id = %s"
                    cursor.execute(sql, id)
                    rows = cursor.fetchall()
                    for row in rows:
                        id_shop = int(row['id'])
            if id_shop == 0:
                return 0
        except:
            return 0
        try:
            with connection.cursor() as cursor: 
                    sql = "SELECT amount FROM Products WHERE name = %s"
                    cursor.execute(sql, name)
                    rows = cursor.fetchall()
                    for row in rows:
                        amount += row['name']
        except Exception:
            amount = amount

        try:
            with connection.cursor() as cursor:
                    cursor.execute('INSERT INTO Products VALUES(%s,%s,%s,%s,%s,%s)',(0, name, price, id_shop, amount, batch))
                    connection.commit()
            with connection.cursor() as cursor: 
                    sql = "SELECT name FROM Shops WHERE owner_id = %s"
                    cursor.execute(sql, id)
                    rows = cursor.fetchall()
                    for row in rows:
                        nam = row['name']
            return nam
        except Exception:
            return 0

def remove_good(name, id, amount):
    connection = getConnection()
    result = []
    if amount == 0:
        try:
            with connection.cursor() as cursor:
                sql = "SELECT id From Shops WHERE owner_id = %s"
                cursor.execute(sql, id)
                rows = cursor.fetchall()
                for row in rows:
                            id_shop = row['id']
            with connection.cursor() as cursor:    
                sql = "DELETE From Products WHERE name = %s AND id_shop = %s"
                cursor.execute(sql, (str(name), int(id_shop)))
                connection.commit()
            with connection.cursor() as cursor:
                sql = "SELECT name From Shops WHERE owner_id = %s"
                cursor.execute(sql, id)
                rows = cursor.fetchall()
                for row in rows:
                            name_shop = row['name']
            result.append(name_shop)
            return result
        except:
            return 0
    else:
        try:
            amount = -int(amount)
            with connection.cursor() as cursor:
                    sql = "SELECT id From Shops WHERE owner_id = %s"
                    cursor.execute(sql, id)
                    rows = cursor.fetchall()
                    for row in rows:
                                id_shop = row['id']
            with connection.cursor() as cursor:
                    sql = "SELECT amount From Products WHERE name = %s"
                    cursor.execute(sql, name)
                    rows = cursor.fetchall()
                    for row in rows:
                                amoun = row['amount']
            amount = amoun + amount
            with connection.cursor() as cursor:    
                    sql = "UPDATE Products SET amount = %s WHERE name = %s AND id_shop = %s"
                    cursor.execute(sql, (int(amount), str(name), int(id_shop)))
                    connection.commit()
            with connection.cursor() as cursor:
                sql = "SELECT name From Shops WHERE owner_id = %s"
                cursor.execute(sql, id)
                rows = cursor.fetchall()
                for row in rows:
                            name_shop = row['name']
            result.append(amount)
            result.append(name_shop)
            return result
        except:
            return 0    

def check_good(name, owner_id):                     
    id_shop = ''
    amount = 0
    am = 0
    connection = getConnection()
    try:
        with connection.cursor() as cursor: 
            sql = "SELECT id FROM Shops WHERE owner_id = %s"
            cursor.execute(sql, str(owner_id))
            rows = cursor.fetchall()
            for row in rows:
                id_shop = row['id']
    except:
        return 0
    try:
        with connection.cursor() as cursor: 
            sql = "SELECT amount FROM Products WHERE name = %s AND id_shop = %s"
            cursor.execute(sql, (name, id_shop))
            rows = cursor.fetchall()
            for row in rows:
                am = row['amount']
            amount = int(am) + int(amount)
            if amount != 0:
                return 0
            else:
                return 1
    except:
        return 0

def add_old_goods(name, id, amount):
    am = 0
    shop_name = ''
    id_shop = 0
    result = []
    connection = getConnection()
    try:
        with connection.cursor() as cursor: 
                        sql = "SELECT name FROM Shops WHERE owner_id = %s"
                        cursor.execute(sql, str(id))
                        rows = cursor.fetchall()
                        for row in rows:
                            shop_name = row['name']
                        result.append(shop_name)
    except:
        return 0
    try:
        with connection.cursor() as cursor: 
                        sql = "SELECT id FROM Shops WHERE owner_id = %s"
                        cursor.execute(sql, str(id))
                        rows = cursor.fetchall()
                        for row in rows:
                            id_shop = row['id']
        with connection.cursor() as cursor: 
                    sql = "SELECT amount FROM Products WHERE name = %s AND id_shop = %s"
                    cursor.execute(sql, (name, id_shop))
                    rows = cursor.fetchall()
                    for row in rows:
                        am = row['amount']
        amount = am + int(amount)
        result.append(amount)
        with connection.cursor() as cursor:
                sql = "UPDATE Products SET amount = %s WHERE id_shop = %s AND name = %s"
                cursor.execute(sql, (int(amount), int(id_shop), str(name)))
                connection.commit()
        
        return result
    except:
        return 0


class MyClient(discord.Client):
    
    async def on_ready(self):
        print('Программа {0} запущена!'.format(self.user))
    
    async def on_message(self, message):
        if message.author != client.user:
            if str(message.channel).find('Direct Message with') != -1:
                guild = client.get_guild(810921714418188330)
                roles = set()
                for role in guild.roles:
                    roles.add(role.id)
                if 845737501293543444 in roles:
                    text = str(message.content)
                    if text == "!help":
                        await message.author.send(
                            ">>> *Список доступных команд:*\n**!make_order:** - заказать товар\n**!create_shop:** - создать магазин\n**!add_goods:** - добавить товар и его цену\n**!remove_good:** - удалить товар из своего магазина или определенное кол-во товара\n**!add_ex_goods:** - добавить товары, имеющиеся в магазине")
                        await message.author.send(">>> *Поля, необходимые для заполнения:*\n**!make_order:** <товар>, <название магазина>, <кол-во товара>\n**!create_shop:** <название магазина>\n**!add_goods:** <товар>, <цена за партию>, <кол-во>, <кол-во товаров в 1 партии>\n**!remove_good:** <товар>, <количество> ***обратите внимание, что второе поле не нужно, если вам надо удалить все товары***\n**!add_ex_goods:** <товар>, <кол-во>")
                        await message.author.send(">>> *Примеры:*\n**!make_order:** Элитры, Timmy's World, 100\n**!create_shop:** Timmy's World\n**!add_goods:** Тотем, 5, 5, 1\n**!remove_good:** Тотем\n**!add_ex_goods:** Незерит, 8")
                        await message.author.send(">>> *Дополнительные команды:*\n**!confirm** - подтверждение заказа\n**!get_order** - заказ получен")
                    elif text.find("!make_order") != -1:
                        id = message.author.id
                        total_information = make_order(text, id)
                        if total_information != 0:
                            text_last.append(text)
                            await message.author.send('>>> Вы собираетесь купить '+ str(total_information[0])+' единиц товара «' + str(total_information[1]) + '».\nИтоговая сумма заказа составляет '+ str(total_information[2])+' АР\nНапишите **!confirm** для подтверждения действия')
                        else:
                            await message.author.send('**Ошибка. Попробуйте еще раз.**')
                    
                    elif text.find('!confirm') != -1:
                        id = message.author.id
                        total_information = make_order(text_last[-1], id)
                        total_information.append(message.author.id)
                        info = confirm_order(total_information)
                        if info != 0:
                            await message.author.send('>>> Спасибо за покупку! Ваш заказ принят, ждите доставки.\nПри получении заказа напишите: **!get_order: <товар>**.')
                            amount = int(info[0][0])
                            product = str(info[0][1])
                            total_price = int(info[0][2])
                            id = int(info[0][-1])
                            user = await client.fetch_user(int(id))
                            msg = 'Вам пришел заказ на ' + str(amount) + ' товара «' + str(product) + '» на сумму ' + str(total_price)+ ' АР'
                            await user.send(msg)
                            result = info[1]
                            channel = client.get_channel(845345224461123619)
                            messages = await channel.history(limit=200).flatten()
                            for msg in messages:
                                res = msg.content
                                if res.find(result[1]) != -1:
                                    delete_to = res[res.find(product):]
                                    delete_to = delete_to[delete_to.find('-'):]
                                    res2 = res[:res.find(delete_to)]
                                    text = res2 + '- ' + str(int(result[0])-int(amount)) + ' штук' + delete_to[delete_to.find('\n'):]
                                    await msg.edit(content = text)
                        else:
                            await message.author.send('**Ошибка заказа. Попробуйте еще раз.**')

                    elif text.find('!get_order:') != -1:
                        id = message.author.id
                        product = text[text.find(':')+2:]
                        res = get_order(id, product)
                        if res != 0:
                            await message.author.send('>>> **Успешно! Спасибо, что вы с нами!**')
                            user = await client.fetch_user(int(res))
                            msg = '>>> Проверьте баланс в банке. Вам начислены АРы за товар.'
                            await user.send(msg)
                        else:
                            await message.author.send('**Ошибка.**')

                    elif text.find('!create_shop') != -1:
                        owner_id = int(message.author.id)
                        name = str(text[text.find(':')+2:])
                        if create_shop(name, owner_id) == 1:
                            await message.author.send('>>> Ваш магазин «' + name + '» успешно зарегистрирован. Теперь вы можете добавить товары.')
                            my_channel = await client.fetch_channel(845345224461123619)
                            msg = await my_channel.send(">>> **----{" + str(name) + "}----**\nПока товаров нет!\nВладелец: <@"+ str(owner_id) +">")
                        else:
                            await message.author.send('**Ошибка. Попробуйте еще раз или проверьте наличие магазина.**')


                    elif text.find('!add_goods:') != -1:
                        if text.find(',') != text.rfind(','):
                            tex = text[text.find(':')+2:]
                            parametres = tex.split(',')
                            name = parametres[0]
                            price = parametres[1]
                            amount = parametres[2]
                            batch = parametres[3]
                            id = message.author.id
                            r = check_good(name, id)
                            if r == 0:
                                await message.author.send('**Проверьте наличие товара в магазине.**')
                            else:
                                result = add_goods(name, price, id, amount, batch)
                                if result != 0:
                                    await message.author.send('>>> Успешно. Товар добавлен в список продаваемых товаров.')
                                    channel = client.get_channel(845345224461123619)
                                    messages = await channel.history(limit=200).flatten()
                                    for msg in messages:
                                        res1 = msg.content.find(str(result))
                                        res = msg.content
                                        if res1 != -1:
                                            if res.find('Пока') == -1:
                                                m = res[:res.find("Владелец")] + name + ': **' + price + '** АР за **'+ batch +'** шт.; в наличии ' +amount + ' штук\n' + res[res.find("Владелец"):]
                                                await msg.edit(content = m)
                                            else:
                                                m = res[:res.find("Пока")] + name + ': **' + price + '** АР за **' + batch + '** шт.; в наличии '+ amount + ' штук\n' + res[res.find("!")+2:]
                                                await msg.edit(content = m)
                                        else:
                                            pass
                                else:
                                    await message.author.send('**Ошибка. Попробуйте еще раз.**')
                        else:
                            await message.author.send('**Ошибка.**')

                    elif text.find('!add_ex_goods:') != -1:
                        if text.find(',') == text.find(','):
                            name = text[text.find(':')+2:text.find(',')]
                            amount = text[text.find(',')+2:]
                            id = message.author.id
                            result = add_old_goods(name, id, amount)
                            if result != 0:
                                await message.author.send('>>> Успешно. Товар добавлен в список продаваемых товаров.')
                                channel = client.get_channel(845345224461123619)
                                messages = await channel.history(limit=200).flatten()
                                for msg in messages:
                                    res1 = msg.content.find(str(result[0]))
                                    res = msg.content
                                    if res1 != -1:
                                        leave2 = res[res.find(name):]
                                        leave1 = res[:res.find(name)]
                                        leave2 = leave2[leave2.find('штук')-1:]
                                        another_part = res[res.find(name):]
                                        position = another_part.find('в наличии ')
                                        another_part = another_part[:position + 10]
                                        m = leave1 + another_part + str(result[1]) + leave2
                                        await msg.edit(content = m)
                                    else:
                                        pass
                            else:
                                await message.author.send('**Ошибка. Попробуйте еще раз.**')
                        else:
                            await message.author.send('**Ошибка.**')

                    elif text.find("!remove_good:") != -1:
                        m = ''
                        id = int(message.author.id)
                        info = text.find(',')
                        if text.find(',') != -1:
                            name = text[text.find(":")+2:text.find(',')]
                            amount = text[text.rfind(',')+2:]
                            result = remove_good(name, id, amount) 
                        else:
                            name = text[text.find(":")+2:]
                            result = remove_good(name, id, 0) 
                        if result != 0:
                            if type(result[0]) != int:
                                await message.author.send(">>> Успешно. Товар удален из списка продаваемых.")
                                channel = client.get_channel(845345224461123619)
                                messages = await channel.history(limit=200).flatten()
                                for msg in messages:
                                    res = msg.content
                                    if res.find(result[0]) != -1:
                                        if res.find(name) != -1:
                                            delete_to = res[res.find(name):]
                                            text = res[:res.find(name)] + delete_to[delete_to.find('\n')+1:]
                                            await msg.edit(content = text)
                                        else:
                                            await message.author.send('**Ошибка. Попробуйте еще раз.**')
                            else:
                                await message.author.send(">>> Успешно. Несколько товаров удалено из списка продаваемых.")
                                channel = client.get_channel(845345224461123619)
                                messages = await channel.history(limit=200).flatten()
                                for msg in messages:
                                    res = msg.content
                                    if res.find(result[1]) != -1:
                                        delete_to = res[res.find(name):]
                                        delete_to = delete_to[delete_to.find('-'):]
                                        res2 = res[:res.find(delete_to)]
                                        text = res2 + ' - ' + str(result[0]) + ' штук' + delete_to[delete_to.find('\n'):]
                                        await msg.edit(content = text)
                        else:
                            await message.author.send('**Ошибка. Попробуйте еще раз.**')
                else:
                    await message.author.send('***Иди нахуй!***')

                
client = MyClient()
client.run(settings['token'])