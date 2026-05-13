import type { FoodTruck } from '../types/truck';

const DESSERT_PATTERN = /디저트|아이스크림|케이크|와플|크레이프|마카롱|도넛|커피|아메리카노|라떼|카페|음료|주스|스무디|버블티|타르트|쿠키|브라우니/;

export function getTruckEmoji(truck: FoodTruck): string {
  const text = [
    truck.name,
    truck.description ?? '',
    ...(truck.menus?.map((m) => m.name) ?? []),
    ...(truck.keywords ?? []),
  ].join(' ');

  return DESSERT_PATTERN.test(text) ? '🍦' : '🍽️';
}
