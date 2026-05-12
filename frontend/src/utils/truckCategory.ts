import type { FoodTruck } from '../types/truck';

type Category =
  | 'taco' | 'pizza' | 'burger' | 'noodle' | 'bunsik'
  | 'coffee' | 'dessert' | 'meat' | 'seafood' | 'japanese'
  | 'chinese' | 'sandwich' | 'chicken' | 'other';

const PATTERNS: [Category, RegExp][] = [
  ['taco',     /타코|부리또|멕시코|살사|파히타/],
  ['pizza',    /피자|pizza/i],
  ['burger',   /버거|햄버거|burger/i],
  ['noodle',   /라면|국수|우동|쌀국수|파스타|스파게티/],
  ['bunsik',   /떡볶이|분식|순대|튀김|어묵|핫도그/],
  ['coffee',   /커피|아메리카노|라떼|카페|음료|주스|스무디/],
  ['dessert',  /아이스크림|디저트|케이크|와플|크레이프|마카롱|도넛/],
  ['meat',     /삼겹살|고기|갈비|스테이크|바비큐|bbq/i],
  ['seafood',  /해산물|새우|오징어|조개|게|랍스터|회|수산/],
  ['japanese', /초밥|스시|일식|돈가스|가츠|라멘/],
  ['chinese',  /짜장|짬뽕|탕수육|만두|중식/],
  ['sandwich', /샌드위치|토스트|베이글|sandwich/i],
  ['chicken',  /치킨|후라이드|양념치킨|닭강정/],
];

const EMOJI: Record<Category, string> = {
  taco:     '🌮',
  pizza:    '🍕',
  burger:   '🍔',
  noodle:   '🍜',
  bunsik:   '🌶️',
  coffee:   '☕',
  dessert:  '🍦',
  meat:     '🥩',
  seafood:  '🦐',
  japanese: '🍱',
  chinese:  '🥟',
  sandwich: '🥪',
  chicken:  '🍗',
  other:    '🍽️',
};

export function getTruckEmoji(truck: FoodTruck): string {
  const text = [
    truck.name,
    truck.description ?? '',
    ...(truck.menus?.map((m) => m.name) ?? []),
    ...(truck.keywords ?? []),
  ].join(' ');

  for (const [category, pattern] of PATTERNS) {
    if (pattern.test(text)) return EMOJI[category];
  }
  return EMOJI.other;
}
