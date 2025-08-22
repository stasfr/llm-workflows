from tg_parsing.parser import map_plain_tg_data, parse_mapped_telegram_data, filter_parsed_telegram_data

def main():
    map_plain_tg_data()
    parse_mapped_telegram_data()
    filter_parsed_telegram_data([], [], [], 3)


if __name__ == "__main__":
    main()
