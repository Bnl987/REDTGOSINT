import sqlite3
from telethon import TelegramClient
from telethon.sync import TelegramClient
from telethon.tl.types import InputMessagesFilterPhotos, InputMessagesFilterVideo
import os
from termcolor import colored

os.system("cls || clear")
print(colored("""


 _______  _______  ______    _________ _______    _______  _______ _________ _       _________
(  ____ )(  ____ \(  __  \   \__   __/(  ____ \  (  ___  )(  ____ \\__   __/( (    /|\__   __/
| (    )|| (    \/| (  \  )     ) (   | (    \/  | (   ) || (    \/   ) (   |  \  ( |   ) (   
| (____)|| (__    | |   ) |     | |   | |        | |   | || (_____    | |   |   \ | |   | |   
|     __)|  __)   | |   | |     | |   | | ____   | |   | |(_____  )   | |   | (\ \) |   | |  
| (\ (   | (      | |   ) |     | |   | | \_  )  | |   | |      ) |   | |   | | \   |   | |   
| ) \ \__| (____/\| (__/  )     | |   | (___) |  | (___) |/\____) |___) (___| )  \  |   | |   
|/   \__/(_______/(______/      )_(   (_______)  (_______)\_______)\_______/|/    )_)   )_(   
                                                                                              


                                   Author: ETHICAL.KULDEEP   Tg: T.me/mrredhu
""", 'blue'))

session_name = 'session_file'

session_exists = os.path.exists(f"{session_name}.session")

if not session_exists:
    try:
        api_id = input("Enter the API ID: ").strip()
    except KeyboardInterrupt:
        print("\nProgram Stopped!")
        exit()
    try:
        api_hash = input("Enter the API Hash: ").strip()
    except KeyboardInterrupt:
        print("\nProgram Stopped!")
        exit()
    try:
        phone_number = input("Enter the phone number (starting with +994):").strip()
    except KeyboardInterrupt:
        print("\nProgram Stopped!")
        exit()
    
    client = TelegramClient(session_name, api_id, api_hash)
    client.start(phone_number)

else:
    api_id = '12345'
    api_hash = '0123456789abcdef0123456789abcdef'
    phone_number = None

client = TelegramClient(session_name, api_id, api_hash)


def create_database():
    try:
        connection = sqlite3.connect('telegram_messages.db')
        cursor = connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            tg_id INTEGER,
            group_name TEXT,
            message_text TEXT,
            message_date TEXT
        )
        ''')

        connection.commit()
        connection.close()
        print("Database successfully created!")
    except sqlite3.Error as error:
        print(f"An error occurred while creating the database: {error}")


def add_message(username, tg_id, group_name, message_text, message_date):
    try:
        connection = sqlite3.connect('telegram_messages.db')
        cursor = connection.cursor()

        cursor.execute('''
        SELECT COUNT(*) FROM messages WHERE message_text = ? AND message_date = ? AND username = ?;
        ''', (message_text, message_date, username))

        message_exists = cursor.fetchone()[0]

        if message_exists == 0:
            cursor.execute('''
            INSERT INTO messages (username, tg_id, group_name, message_text, message_date)  
            VALUES (?, ?, ?, ?, ?);
            ''', (username, tg_id, group_name, message_text, message_date))

            connection.commit()

            with open(f"{username}_messages.txt", "a", encoding="utf-8") as file:
                file.write(f"Group: {group_name}\n")
                file.write(f"Message: {message_text}\n")
                file.write(f"Date: {message_date}\n")
            print(f"New message added: {group_name}")
        else:
            print(f"Message already exists: {group_name}")

        connection.close()
    except sqlite3.Error as error:
        print(f"An error occurred while adding the message to the database: {error}")
    except Exception as error:
        print(f"Error: {error}")


async def collect_messages(search_value):
    try:
        if phone_number:
            await client.start(phone_number)
        else:
            await client.start()

        dialogs = await client.get_dialogs()

        for dialog in dialogs:
            if dialog.is_group:
                group_name = dialog.name
                group_id = dialog.id

                print(f"Searching messages in group: {group_name}...")
                messages = await client.get_messages(dialog.id, from_user=search_value, limit=10000000)

                for message in messages:
                    tg_id = message.sender_id
                    add_message(str(search_value), tg_id, group_name, message.text, str(message.date))

        print("Search completed. Messages saved in database and text file.")
    except Exception as error:
        print(f"An error occurred while connecting with Telegram: {error}")


async def collect_group_info(group_link):
    try:
        if phone_number:
            await client.start(phone_number)
        else:
            await client.start()

        group = await client.get_entity(group_link)
        group_name = group.title
        group_description = group.about if hasattr(group, 'about') and group.about else "No information"

        group_summary = (
            f"Group ID: {group.id}\n"
            f"Creator: {'Yes' if group.creator else 'No'}\n"
            f"Verified: {'Yes' if group.verified else 'No'}\n"
            f"Number of members: {len(await client.get_participants(group))} members\n"
            f"Mega Group: {'Yes' if group.megagroup else 'No'}\n"
            f"Group Link: {group.username or 'No information'}\n"
        )

        print(f"Collecting information for group: {group_name}...")

        members = await client.get_participants(group)

        with open(f"{group_name}_info.txt", "w", encoding="utf-8") as file:
            file.write("🛡️ Group Information 🛡️\n")
            file.write(f"Group Name    : {group_name}\n")
            file.write(f"Group Description : {group_description}\n")
            file.write(f"Group Summary:\n{group_summary}\n")
            file.write(f"Number of members: {len(members)} members\n")
            file.write("=" * 50 + "\n\n")

            for idx, member in enumerate(members, start=1):
                file.write(f"Member #{idx}:\n")
                file.write(f"  Full Name    : {member.first_name or ''} {member.last_name or ''}\n")
                file.write(f"  Telegram ID  : {member.id}\n")
                file.write(f"  Phone Number : {member.phone or 'No information'}\n")
                file.write(f"  Status       : {'Bot' if member.bot else 'User'}\n")
                file.write("-" * 50 + "\n")

        print(f"Group information saved to: {group_name}_info.txt")
    except Exception as error:
        print(f"An error occurred while collecting group information: {error}")


async def collect_message_stats(search_value):
    try:
        if phone_number:
            await client.start(phone_number)
        else:
            await client.start()

        dialogs = await client.get_dialogs()
        message_counts = {}

        for dialog in dialogs:
            if dialog.is_group:
                group_name = dialog.name
                print(f"Analyzing group: {group_name}...")
                messages = await client.get_messages(dialog.id, from_user=search_value, limit=10000000)

                if len(messages) > 0:
                    message_counts[group_name] = len(messages)

        print(f"\nMessage statistics for user '{search_value}':")

        with open(f"{search_value}_message_statistics.txt", "a", encoding="utf-8") as file:
            file.write(f"User: {search_value}\n")
            file.write("Group Name - Message Count\n")
            file.write("=" * 30 + "\n")

            for group, count in message_counts.items():
                print(f"Group: {group} - Message Count: {count}")
                file.write(f"Group: {group} - Message Count: {count}\n")

            file.write("=" * 30 + "\n")
        print(f"Statistics saved to: {search_value}_message_statistics.txt")

    except Exception as error:
        print(f"Error: {error}")


async def download_group_media(group_link):
    try:
        group = await client.get_entity(group_link)

        messages = await client.get_messages(group, limit=5000, filter=InputMessagesFilterPhotos)
        messages += await client.get_messages(group, limit=5000, filter=InputMessagesFilterVideo)

        print(f"Downloading media from group: {group_link}...")

        for message in messages:
            if message.media:
                media_file = await client.download_media(message.media, file="media_downloads/")
                print(f"Downloaded: {media_file}")
            else:
                print(f"No media in message: {message.id}")

    except Exception as error:
        print(f"An error occurred: {error}")


def restart_program():
    while True:
        choice = input("Would you like to add a new target? (Yes/No): ").strip().lower()
        if choice == "yes":
            with client:
                try:
                    new_choice = input("Select search type (1: Username, 2: ID): ").strip()
                    if new_choice == '1':
                        search_value = input("Enter the Telegram username: ").strip()
                    elif new_choice == '2':
                        search_value = int(input("Enter the Telegram user ID: ").strip())
                    else:
                        print("Invalid selection! Program will stop.")
                        exit(1)

                    client.loop.run_until_complete(collect_messages(search_value))
                except Exception as error:
                    print(f"Error: {error}")
        elif choice == "no":
            print("Program stopped...")
            break
        else:
            print("Please enter 'Yes' or 'No'.")


def main_menu():
    while True:
        print(colored("\nSILVERTGOSINT MENU:", 'white'))
        print("1. Collect user messages")
        print("2. Collect group info")
        print("3. Collect user message statistics")
        print("4. Download all media in group")
        print("5. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            with client:
                try:
                    print("Search type:")
                    print("1. Username")
                    print("2. Telegram ID")
                    search_type = input("Select option: ").strip()

                    if search_type == "1":
                        search_value = input("Enter the Telegram username: ").strip()
                    elif search_type == "2":
                        search_value = int(input("Enter the Telegram user ID: ").strip())
                    else:
                        print("Invalid choice! Going back...")
                        continue

                    client.loop.run_until_complete(collect_messages(search_value))
                except Exception as error:
                    print(f"Error: {error}")
        elif choice == "2":
            with client:
                try:
                    group_link = input("Enter the group link: ").strip()
                    client.loop.run_until_complete(collect_group_info(group_link))
                except Exception as error:
                    print(f"Error: {error}")
        elif choice == "3":
            with client:
                try:
                    search_type = input("Select search type (1: Username, 2: ID): ").strip()

                    if search_type == "1":
                        search_value = input("Enter the Telegram username: ").strip()
                    elif search_type == "2":
                        search_value = int(input("Enter the Telegram user ID: ").strip())
                    else:
                        print("Invalid choice! Going back...")
                        continue

                    client.loop.run_until_complete(collect_message_stats(search_value))
                except Exception as error:
                    print(f"Error: {error}")
        elif choice == "4":
            with client:
                try:
                    group_link = input("Enter the group link: ").strip()
                    client.loop.run_until_complete(download_group_media(group_link))
                except Exception as error:
                    print(f"Error: {error}")
        elif choice == "5":
            print("Exiting program...")
            break
        else:
            print("Invalid choice! Please make a correct selection.")

create_database()
main_menu()
restart_program()
