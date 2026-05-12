export interface Menu {
  id?: number;
  name: string;
  price: number;
}

export interface OwnerBrief {
  id: number;
  nickname: string;
}

export interface FoodTruck {
  id: number;
  name: string;
  description?: string;
  latitude: number;
  longitude: number;
  is_open: boolean;
  avg_rating: number;
  review_count: number;
  representative_menu?: string;
  account_info?: string;
  image_url?: string;
  menus: Menu[];
  owner?: OwnerBrief;
  keywords?: string[];
}

export interface LatLng {
  lat: number;
  lng: number;
}
