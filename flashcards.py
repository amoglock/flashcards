import io
import random
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--import_from')
parser.add_argument('--export_to')
args = parser.parse_args()

log_file = io.StringIO()

cards = dict()
new_dict = dict()
commands = ('add', 'remove', 'import', 'export', 'ask', 'exit', 'log', 'hardest card', 'reset stats')


def logging_action(message):
    log_file.write(message + '\n')


class Flashcard:
    def __init__(self, term, definition):
        self.term = term
        self.definition = definition

    def __str__(self):
        logging_action(f'The pair ("{self.term}":"{self.definition}") has been added.')
        return f'The pair ("{self.term}":"{self.definition}") has been added.\n'


class CheckError(Exception):
    def __init__(self, word):
        self.message = f'The {word} already exists. Try again:'
        super().__init__(self.message)
        logging_action(self.message)


def menu():
    if args.import_from:
        import_(args.import_from)
    while True:
        print('Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):')
        logging_action('Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):')
        action = input()
        logging_action(action)
        if action in commands:
            if action == 'add':
                add()
            if action == 'export':
                export(file=None)
            if action == 'import':
                import_(file=None)
            if action == 'remove':
                remove()
            if action == 'ask':
                ask()
            if action == 'log':
                logging()
            if action == 'hardest card':
                try:
                    max_errors = max([cards[key]['errors'] for key in cards.keys()])
                    names_of_cards = ['"' + key + '"' for key in cards.keys() if cards[key]['errors'] == max_errors]
                    sum_errors = sum([cards[key]['errors'] for key in cards.keys() if cards[key]['errors'] == max_errors])
                    hardest_card(names_of_cards, sum_errors)
                except:
                    print('There are no cards with errors.\n')
                    logging_action('There are no cards with errors.')
            if action == 'reset stats':
                reset_stats()
            if action == 'exit':
                if args.export_to:
                    export(args.export_to)
                print('Bye bye!')
                logging_action('Bye bye!')
                break
        else:
            print("Wrong command! Please use 'add', 'remove', 'import', 'export', 'ask', 'exit'.\n")
            logging_action("Wrong command! Please use 'add', 'remove', 'import', 'export', 'ask', 'exit'.")


def add_term():
    print('The card:')
    logging_action('The card:')
    while True:
        try:
            term = input()
            logging_action(term)
            if term in cards:
                raise CheckError('term')
            return term
        except CheckError as err:
            print(err)
            continue


def add_definition():
    print('The definition of the card:')
    logging_action('The definition of the card:')
    while True:
        try:
            definition = input()
            logging_action(definition)
            new_dict_create()
            if definition in new_dict.values():
                raise CheckError('definition')
            return definition
        except CheckError as err:
            print(err)
            continue


def add():
    term = add_term()
    definition = add_definition()
    cards[term] = {'definition': definition, 'errors': 0}
    print(Flashcard(term, definition))


def export(file):
    if file:
        file_name = file
    else:
        file_name = input('File name:\n')
    logging_action(file_name)
    with open(f'{file_name}', 'a', encoding='utf-8') as file:
        for key, value in cards.items():
            list_for_write = list()
            list_for_write.append(key)
            for v in value.values():
                list_for_write.append(v)
            file.write(f'{str(list_for_write)}\n')
    print(len(cards), 'cards have been saved.')
    logging_action(str(len(cards)) + ' cards have been saved.')


def import_(file):
    if file:
        file_name = file
    else:
        file_name = input('File name:\n')
    logging_action(file_name)
    if os.access(file_name, os.R_OK):
        with open(f'{file_name}', 'r', encoding='utf-8') as file:
            added_cards = 0
            for line in file:
                new_list = line.strip('[]\n').split(', ')
                dict_list = list()
                for new_line in new_list:
                    dict_list.append(new_line.strip('\''))
                cards[dict_list[0]] = {'definition': dict_list[1], 'errors': int(dict_list[2])}
                added_cards += 1
        print(f'{added_cards} cards have been loaded.')
        logging_action(f'{added_cards} cards have been loaded.')
    else:
        print('File not found.\n')
        logging_action('File not found.')


def remove():
    term_card = input('Which card?\n')
    logging_action(term_card)
    if term_card in cards:
        del cards[term_card]
        print('The card has been removed.\n')
        logging_action('The card has been removed.')
    else:
        print(f'Can\'t remove "{term_card}": there is no such card.\n')
        logging_action(f'Can\'t remove "{term_card}": there is no such card.')


def ask():
    asked = 0
    try:
        number = int(input('How many times to ask?\n'))
        logging_action(str(number))
    except ValueError:
        logging_action("Please use a integer!")
        return print("Please use a integer!")
    new_dict_create()
    while asked < number:
        term = random.choice(list(cards))
        question = input(f'Print the definition of "{term}": \n')
        logging_action(question)
        definition = cards[term]['definition']
        if question == definition:
            print('Correct!')
            logging_action('Correct!')
        elif question in new_dict.values():
            termine = find_key(question)
            print(f'Wrong. The right answer is "{definition}", but your definition is correct for "{termine}".')
            cards[term]['errors'] += 1
            logging_action(f'Wrong. The right answer is "{definition}", but your definition is correct for "{termine}".')
        else:
            print(f'Wrong. The right answer is "{cards[term]["definition"]}".')
            cards[term]['errors'] += 1
            logging_action(f'Wrong. The right answer is "{cards[term]["definition"]}".')
        asked += 1
    print()


def logging():
    file_name = input('File name:\n')
    logging_action('File name: ')
    content = log_file.getvalue()
    with open(f'{file_name}', 'w') as file:
        print(content, file=file)
        print('The log has been saved.')
        print('The log has been saved.', file=file)


def hardest_card(cards_names, errors):
    if errors:
        print(f"The hardest card is {', '.join(cards_names)}.  You have {errors} errors answering it.")
        logging_action(f"The hardest card is {', '.join(cards_names)}.  You have {errors} errors answering it.")
    else:
        print('There are no cards with errors.\n')
        logging_action('There are no cards with errors.')


def reset_stats():
    for key in cards.keys():
        cards[key]['errors'] = 0
    print('Card statistics have been reset.')
    logging_action('Card statistics have been reset.')


def new_dict_create():
    for key, value in cards.items():
        new_dict[key] = value['definition']


def find_key(string):
    for key, value in new_dict.items():
        if string == value:
            return key


if __name__ == "__main__":
    menu()