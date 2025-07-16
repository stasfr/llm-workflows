import { chain } from 'stream-chain';
import parser from 'stream-json';
import Pick from 'stream-json/filters/Pick.js';
import StreamArray from 'stream-json/streamers/StreamArray.js';

import { createReadStream } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const WORDS_OFFSET = 3;

// const normalizedDataBaseMap = new Map<string, number>();
const dataBaseMap = new Map<string, number>();

interface Post { text: string; }

function isPost(value: unknown): value is Post {
  if (value === null || typeof value !== 'object') {
    return false;
  }

  return 'text' in value && typeof (value as { text: unknown }).text === 'string';
}

const GARBAGE_LIST: string[] = [
  'Предложить новость ⬅️ \nРезервный канал ⬅️',
  'Заявка на вступление ⬅️\nПредложить новость\\Реклама - @zheldor_admin',
  'Заявка на вступление ⬅️\nПредложить новость - @zheldor_admin',
  'Вступить тут ⬅️\nПредложить новость\\Реклама - @zheldor_admin',
  'Ссылки для вступления тут ⬅️\nПредложить новость\\Реклама - @zheldor_admin',
  'Ссылки для вступления тут ⬅️\nНаш второй канал: ➡️ Барахолка ⬅️\nПредложить новость\\Реклама - @zheldor_admin',
  'новость - @zheldor_admin',
  'Наш второй канал: ➡️ Барахолка ⬅️\nПредложить новость\\Реклама - @zheldor_admin',
  'НЕ ПИШЕМ ИНФОРМАЦИЮ: ЧТО/КУДА/ОТКУДА ЛЕТЕЛО. МГНОВЕННЫЙ БАН.',
  'про наш второй канал: Барахолка Железнодорожный',
  '\n______________________________________\n',
  '\n_____________________________________\n',
  '\n____________________________________\n',
  '\n_________________________________\n',
  '\n________________________________\n',
  '\n___________________________\n',
  '\n_________________________\n',
  '\n________________________\n',
  '\n_______________________\n',
  '\n______________________\n',
  '\n_____________________\n',
  '\n____________________\n',
  '\n___________________\n',
  '\n__________________\n',
  '\n_________________\n',
  '\n________________\n',
  '\n_______________\n',
  '\n______________\n',
  '\n_____________\n',
  '\n____________\n',
  '\n___________\n',
  '\n__________\n',
  '\n_________\n',
  '\n______\n',
  '\n____\n',
  '\n___\n',
  '\n__\n',
  '\n_\n',
  'где вы можете продать и купить б/у (и новые) вещи, технику и иные предметы.\n\n⬇️ ССЫЛКА ⬇️\nhttps://t.me/+2-05d22f7f4zN2Ey\n\nПодать объявление - @baraholka_adm \nТолько частные продажи, не коммерция ❌',
];

const GARBAGE_POSTS_LIST: string[] = [
  'Маяковского 24а \nUP Луговая 14к1\nТел.',
  'Подписаться на канал ПУТЁВЫЙ✔\n- Кликнуть',
  'разрядов и званий\n-подготовка с НУЛЯ\n-профилактика',
  '79771106050',
  '8-926-319-96-17 Отрада Окна',
  'https://t.me/justeatsu',
  '+7(916)426-60-37',
  '89263951101',
  'ExcursiiJeldor',
  '89209065025',
  '+7 (925) 721-98-82',
  '+7 (926) 292-92-11',
  'modnaya_shtora',
  '7(926)117-66-55',
  'stroitrakt',
  'Внимание, розыгрыш для жителей Железнодорожного',
  'систему обратного осмоса для фильтрации питьевой',
  'предельно просты:\n⠀\n✅Быть участником группы - Сантехник',
  '89913080091',
  '84951960091',
  'friends_zagorodnyi_club',
  'fishstore_zheldor',
  'M0eifQxV0phjNjhi',
  'на собственном предприятии вкусную рыбку, солим,',
  'permanentgarage',
  '7 (495) 369-60-91',
  '7 (495) 369-60-92',
  '7 (495) 181-85-15',
  'DomVISMUTZheldor',
  '7 962 98 13 660',
  '89851826969',
  '8-495-363-59-53',
  'FREYA',
  '8 (901) 798-98-91',
  'natasha_tetery',
  'вас на бесплатные лекции в «Балашихинский',
  'ПУТЁВЫЙ',
  'Путёвый',
  '79857944134',
  '8(977)419-54-85',
  'beauty_domik',
  'kursy_v_zheleznodorozhnom',
  '60460047077',
  'estetika.artstudio',
  '79646441943',
  '8 (499) 499-99-23',
  'с 10:00 до 23:00 во всех',
  'В транспортную компанию на склад требуются',
  'elbody.tilda.ws',
  'tuningtela_balashiha',
  '7(919)100-89-00',
  '89250200909',
  'ЛИКВИДАЦИЯ склада дверей входных и межкомнатных',
  '7(499)7034004',
  '7(916)030-74-68',
  'studio_vestra',
  '8-905-555-90-40',
  'kraski.jeleznodorojniy',
  'fcdynamika',
  'zd.farm',
  '89163844068',
  '89776163393',
  '79661895634',
  '8 964 624 82 22',
  '7 (925) 313-44-04',
  '89859276777',
  '7(495) 649-82-05',
  'baraholka_adm',
  'OtradaOkna',
  'SIRIUS',
  '79646248222',
  '79253553557',
  '79162648003',
  '79000751453',
  '89060312822',
  'CCUHIPX4oA',
  '84994994248',
  '89385349451',
  'ПроСилуэт',
  '7 (495) 988-92-98',
  'kuhni_renessans',
  '89162237250',
  '8-498-602-20-74',
  'СтройТракт',
  'malyavochki_kids',
  'VaPadhT8y7FVqp3m',
  '7 (929) 570 78 81',
  'Мы — канал Путешествия и туризм!',
  '8(926)040-47-92',
  'кухни от 40000 р.\n\n📌 БЕСПЛАТНО замер, 3d проект и доставка',
  '8(985)889-64-77',
  '8(499) 226-17-86',
  'UPfitness',
  'club214464770',
  'personaltulip',
  '7 916 467 61 41',
  'рельсы в метро. Лучше посмотреть полностью.\n\n✅ Спойлер: ложитесь между рельс,',
];

function replaceGarbage(sourceStr: string): string {
  let cleanStr = sourceStr;

  if (!GARBAGE_LIST.length) {
    return cleanStr;
  }

  GARBAGE_LIST.forEach((garbage) => {
    cleanStr = cleanStr.replace(garbage, '');
  });

  return cleanStr;
}

function buildNgramMap(sourceStr: string, dataBaseMap: Map<string, number>): void {
  const postIsGarbage = GARBAGE_POSTS_LIST.some((garbage) => sourceStr.includes(garbage));

  if (postIsGarbage) {
    return;
  }

  const ungarbageStr = replaceGarbage(sourceStr.trim());

  const normalizedStr = ungarbageStr
    .split(' ')
    .filter(Boolean);

  const firstIndex = 0;
  const lastIndex = normalizedStr.length - WORDS_OFFSET;

  for (let index = firstIndex; index <= lastIndex; index++) {
    const entrySlice = normalizedStr.slice(index, index + WORDS_OFFSET);
    const entryKey = entrySlice.join(' ');

    const currentCount = dataBaseMap.get(entryKey) ?? 0;
    dataBaseMap.set(entryKey, currentCount + 1);
  }
}

// function buildNormalizedNgramMap(sourceStr: string, normalizedDataBaseMap: Map<string, number>): void {
//   const normalizedStr = sourceStr
//     .replace(/[^а-яА-ЯёЁ ]/g, ' ')
//     .trim()
//     .split(' ')
//     .filter(Boolean)
//     .map((word) => word.toLocaleLowerCase());

//   const firstIndex = 0;
//   const lastIndex = normalizedStr.length - WORDS_OFFSET;

//   for (let index = firstIndex; index <= lastIndex; index++) {
//     const entrySlice = normalizedStr.slice(index, index + WORDS_OFFSET);
//     const entryKey = entrySlice.join(' ');

//     const currentCount = normalizedDataBaseMap.get(entryKey) ?? 0;
//     normalizedDataBaseMap.set(entryKey, currentCount + 1);
//   }
// }

async function processJsonStream(filePath: string): Promise<Map<string, number>> {
  const pipeline = chain([
    createReadStream(filePath),
    parser(),
    new Pick({ filter: 'posts' }),
    new StreamArray(),
  ]);

  try {
    for await (const { value } of pipeline) {
      if (isPost(value)) {
        buildNgramMap(value.text, dataBaseMap);
        // buildNormalizedNgramMap(value.text, normalizedDataBaseMap);
      }
    }

    return dataBaseMap;
  } catch (err) {
    console.error('Stream processing error:', err);
    throw err;
  }
}

// --- Main execution ---
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const dataFilePath = join(__dirname, '..', 'plain_data', 'posts.json');

export async function indexText(): Promise<[string, number][]> {
  const dataBaseMap = await processJsonStream(dataFilePath);

  const exceptions = [
    '🌸 Афиша мероприятий в Пестовском парке',
    'ГСУ СК России по Московской области',
    'Афиша мероприятий в Пестовском парке на',
    '000 000 000 000 000 000',
    'не сидите и не лежите на',
    'сидите и не лежите на траве',
    '№ 34к «ЖК Центр-2 - платф.',
    '34к «ЖК Центр-2 - платф. Ольгино»',
    'Художественная фантазия на тему постапокалипсиса, все совпадения случайны',
    'фантазия на тему постапокалипсиса, все совпадения',
    'Горячая линия работает круглосуточно , принимает',
    'должен был бороться со злом, а',
    'был бороться со злом, а не',
    'бороться со злом, а не примкнуть',
    'со злом, а не примкнуть к',
    'ваша вечеринка не похожа на эту…',
    'появятся большая прогулочная зона, две детские игровые площадки, тренажеры для',
    'большая прогулочная зона, две детские игровые площадки, тренажеры для занятий',
    'прогулочная зона, две детские игровые площадки, тренажеры для занятий спортом',
    'должен был бороться со злом, а не примкнуть к нему!',
    'зона, две детские игровые площадки, тренажеры для занятий спортом на',
    'две детские игровые площадки, тренажеры для занятий спортом на открытом',
  ];

  console.log([...dataBaseMap.entries()].length);

  const sortedDataBase = [...dataBaseMap.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10 + exceptions.length)
    .filter((entry) => !exceptions.includes(entry[0]));

  console.log('Top 10 n-grams:');
  console.log(sortedDataBase);

  return sortedDataBase;
}
