import random
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Character class and other code...

class Character:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.gold = 0
        self.inventory = []
        self.messages_sent = 0

    def add_gold(self, amount):
        self.gold += amount

    def add_item_to_inventory(self, item):
        self.inventory.append(item)

def level_up(character):
    if character.messages_sent % 200 == 0:
        character.level += 1

# Command handlers...

def startrpg(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the RPG Bot!")

def help(update, context):
    help_text = """
    Available commands:
    /startrpg - Start the bot
    /choose - Choose a character
    /help - Show the help message
    /create - Create a character
    /fight - Fight an enemy
    /balance - Check your balance
    /shop - Visit the shop
    /inventory - View your inventory
    /daily - Claim daily reward
    /weekly - Claim weekly reward
    /buy - Buy an item from the shop
    /gift - Gift an item to another player
    /marry - Get married (requires level 10)
    /build - Build an item (e.g., /build house)
    /hunt - Hunt an animal
    /sell - Sell a hunted animal
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

def choose(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please choose a character.")

def create(update, context):
    args = context.args
    if len(args) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a name for your character.")
    else:
        name = ' '.join(args)
        character = Character(name)
        context.user_data['character'] = character
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Character {name} created successfully!")

def fight(update, context):
    character = context.user_data.get('character')
    if character is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't created a character yet. Use /create to create one.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You are fighting an enemy!")

def balance(update, context):
    character = context.user_data.get('character')
    if character is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't created a character yet. Use /create to create one.")
    else:
        balance_text = f"Your current balance is {character.gold} gold coins."
        context.bot.send_message(chat_id=update.effective_chat.id, text=balance_text)

def shop(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the shop!")

def inventory(update, context):
    character = context.user_data.get('character')
    if character is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't created a character yet. Use /create to create one.")
    else:
        inventory_text = f"Your inventory: {', '.join(character.inventory)}"
        context.bot.send_message(chat_id=update.effective_chat.id, text=inventory_text)

def daily(update, context):
    character = context.user_data.get('character')
    if character is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't created a character yet. Use /create to create one.")
    else:
        last_daily_claim = context.user_data.get('last_daily_claim')
        if last_daily_claim is not None and datetime.now() - last_daily_claim < timedelta(days=1):
            context.bot.send_message(chat_id=update.effective_chat.id, text="You have already claimed your daily reward.")
        else:
            # Give the daily reward
            reward = 50  # Set the daily reward amount
            character.add_gold(reward)
            context.user_data['last_daily_claim'] = datetime.now()
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"You claimed your daily reward of {reward} gold coins.")

def weekly(update, context):
    character = context.user_data.get('character')
    if character is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't created a character yet. Use /create to create one.")
    else:
        last_weekly_claim = context.user_data.get('last_weekly_claim')
        if last_weekly_claim is not None and datetime.now() - last_weekly_claim < timedelta(weeks=1):
            context.bot.send_message(chat_id=update.effective_chat.id, text="You have already claimed your weekly reward.")
        else:
            # Give the weekly reward
            reward = 200  # Set the weekly reward amount
            character.add_gold(reward)
            context.user_data['last_weekly_claim'] = datetime.now()
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"You claimed your weekly reward of {reward} gold coins.")

def buy(update, context):
    args = context.args
    if len(args) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide an item to buy.")
    else:
        item_name = ' '.join(args)
        character = context.user_data.get('character')
        if character is None:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't created a character yet. Use /create to create one.")
        else:
            # Check if the item is available in the shop and deduct the gold
            item_cost = 50  # Set the cost of the item
            if character.gold >= item_cost:
                character.gold -= item_cost
                character.add_item_to_inventory(item_name)
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"You bought {item_name} for {item_cost} gold coins.")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Insufficient gold.")

def gift(update, context):
    args = context.args
    if len(args) < 2:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide the recipient and item to gift.")
    else:
        recipient = args[0]
        item_name = ' '.join(args[1:])
        character = context.user_data.get('character')
        if character is None:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't created a character yet. Use /create to create one.")
        else:
            if item_name in character.inventory:
                character.inventory.remove(item_name)
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"You gifted {item_name} to {recipient}.")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have that item to gift.")

def marry(update, context):
    character = context.user_data.get('character')
    if character is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't created a character yet. Use /create to create one.")
    else:
        level = character.level  # Replace with the appropriate way to get the character's level
        if level >= 10:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Congratulations! You are now married.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You need to be at least level 10 to get married.")

def build(update, context):
    args = context.args
    if len(args) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide the item to build.")
    else:
        item_name = ' '.join(args)
        character = context.user_data.get('character')
        if character is None:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't created a character yet. Use /create to create one.")
        else:
            if item_name == "house":
                house_cost = 100  # Set the cost of building a house
                if character.gold >= house_cost:
                    character.gold -= house_cost
                    character.add_item_to_inventory("House")
                    context.bot.send_message(chat_id=update.effective_chat.id, text="You have built a house!")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Insufficient gold.")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid item to build.")

def hunt(update, context):
    character = context.user_data.get('character')
    if character is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't created a character yet. Use /create to create one.")
    else:
        animal_list = ["rabbit", "deer", "wolf"]  # List of animals to hunt
        animal = random.choice(animal_list)
        context.user_data['animal'] = animal
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"You are hunting a {animal}!")

def sell(update, context):
    character = context.user_data.get('character')
    if character is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't created a character yet. Use /create to create one.")
    else:
        animal = context.user_data.get('animal')
        if animal is None:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't hunted any animal yet. Use /hunt to hunt an animal.")
        else:
            # Sell the hunted animal and add gold to the character
            animal_price = {'rabbit': 10, 'deer': 20, 'wolf': 30}  # Set the prices for each animal
            price = animal_price.get(animal, 0)
            character.add_gold(price)
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"You sold the {animal} for {price} gold coins.")
            context.user_data.pop('animal')

def message_handler(update, context):
    character = context.user_data.get('character')
    if character is not None:
        character.messages_sent += 1
        level_up(character)

# Create the updater and add handlers...

def main():
    updater = Updater("5641185391:AAH3YaOJWxfPDqu4m8bWRM-tnhhBEcQ0KoU", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("choose", choose))
    dp.add_handler(CommandHandler("create", create))
    dp.add_handler(CommandHandler("fight", fight))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("shop", shop))
    dp.add_handler(CommandHandler("inventory", inventory))
    dp.add_handler(CommandHandler("daily", daily))
    dp.add_handler(CommandHandler("weekly", weekly))
    dp.add_handler(CommandHandler("buy", buy))
    dp.add_handler(CommandHandler("gift", gift))
    dp.add_handler(CommandHandler("marry", marry))
    dp.add_handler(CommandHandler("build", build))
    dp.add_handler(CommandHandler("hunt", hunt))
    dp.add_handler(CommandHandler("sell", sell))

    dp.add_handler(MessageHandler(Filters.text, message_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()





