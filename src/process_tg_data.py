from tg_parsing.parser import parse_raw_telegram_data, filter_parsed_telegram_data

def process_tg_data():
    print('Parsing and filtering Telegram Data')
    parse_raw_telegram_data()
    filter_parsed_telegram_data([], [], [], 3)

if __name__ == "__main__":
    process_tg_data()
