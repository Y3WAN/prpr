import { useEffect, useState } from 'react';
import type { LatLng } from '../../types/truck';
import { truckApi } from '../../services/truckApi';
import { useMapStore } from '../../stores/mapStore';

interface Props {
  center: LatLng;
}

// undefined = 로딩 중, null = 전체 트럭 없음, LatLng = 최근접 위치
type NearestState = LatLng | null | undefined;

function reverseGeocode(loc: LatLng): Promise<string> {
  return new Promise((resolve, reject) => {
    if (!window.kakao?.maps?.services) {
      reject(new Error('Kakao services not loaded'));
      return;
    }
    const geocoder = new window.kakao.maps.services.Geocoder();
    geocoder.coord2RegionCode(loc.lng, loc.lat, (result: any[], status: string) => {
      if (status !== window.kakao.maps.services.Status.OK || !result.length) {
        reject(new Error('Geocoding failed'));
        return;
      }
      // region_type 'H'(행정동) 우선, 없으면 첫 번째
      const r = result.find((item: any) => item.region_type === 'H') ?? result[0];
      const name = [r.region_2depth_name, r.region_3depth_name].filter(Boolean).join(' ');
      resolve(name || r.address_name);
    });
  });
}

export const NoTrucksNearby = ({ center }: Props) => {
  const { setCenter } = useMapStore();
  const [nearest, setNearest] = useState<NearestState>(undefined);
  const [areaName, setAreaName] = useState<string | null>(null);

  useEffect(() => {
    setNearest(undefined);
    setAreaName(null);

    truckApi.nearest(center.lat, center.lng)
      .then(({ data }) => {
        if (data.latitude == null || data.longitude == null) {
          setNearest(null);
          return;
        }
        const loc: LatLng = { lat: data.latitude, lng: data.longitude };
        setNearest(loc);
        reverseGeocode(loc).then(setAreaName).catch(() => setAreaName(null));
      })
      .catch(() => setNearest(null));
  }, [center.lat, center.lng]);

  return (
    <div className="no-trucks-banner">
      <span className="no-trucks-banner__icon">🚚</span>
      <p className="no-trucks-banner__msg">주변에 영업 중인 푸드트럭이 없습니다.</p>

      {nearest === undefined && (
        <p className="no-trucks-banner__sub">가까운 구역을 찾는 중…</p>
      )}

      {nearest !== undefined && nearest !== null && (
        <>
          <p className="no-trucks-banner__sub">
            가장 가까운 활성화 구역은{' '}
            <strong>{areaName ?? '…'}</strong>입니다.
          </p>
          <button
            className="no-trucks-banner__btn"
            onClick={() => setCenter(nearest)}
          >
            이동하기
          </button>
        </>
      )}

      {nearest === null && (
        <p className="no-trucks-banner__sub">현재 영업 중인 푸드트럭이 없습니다.</p>
      )}
    </div>
  );
};
