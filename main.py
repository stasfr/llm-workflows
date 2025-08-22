from tg_parsing.parser import parse_raw_telegram_data, filter_parsed_telegram_data

def main():
    parse_raw_telegram_data()
    filter_parsed_telegram_data([], [], [], 3)


if __name__ == "__main__":
    main()
