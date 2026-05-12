import { useEffect, useState } from 'react';
import { truckApi } from '../services/truckApi';
import type { FoodTruck, Menu } from '../types/truck';
import { MenuInputList } from '../components/truck/MenuInputList';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { showToast } from '../components/common/Toast';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { LocationPickerMap } from '../components/map/LocationPickerMap';
import { useLocationStore } from '../stores/locationStore';

const TruckManagePage = () => {
  const [truck, setTruck] = useState<FoodTruck | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [menuSaving, setMenuSaving] = useState(false);
  const { userLocation, requestLocation } = useLocationStore();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [accountInfo, setAccountInfo] = useState('');
  const [lat, setLat] = useState('');
  const [lng, setLng] = useState('');
  const [menus, setMenus] = useState<Menu[]>([{ name: '', price: 0 }]);
  const [editMenus, setEditMenus] = useState<Menu[]>([{ name: '', price: 0 }]);

  useEffect(() => {
    truckApi.my()
      .then(({ data }) => {
        setTruck(data);
        setName(data.name);
        setDescription(data.description ?? '');
        setAccountInfo(data.account_info ?? '');
        setLat(String(data.latitude));
        setLng(String(data.longitude));
        setMenus(data.menus.length > 0 ? data.menus : [{ name: '', price: 0 }]);
        setEditMenus(data.menus.length > 0 ? data.menus : [{ name: '', price: 0 }]);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (userLocation && !truck) {
      setLat(String(userLocation.lat));
      setLng(String(userLocation.lng));
    }
  }, [userLocation]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (menus.some((m) => !m.name.trim())) {
      showToast('모든 메뉴명을 입력해주세요.', 'warning');
      return;
    }
    setSaving(true);
    try {
      const { data } = await truckApi.create({
        name,
        menus: menus.map((m) => ({ name: m.name, price: m.price })),
        latitude: Number(lat),
        longitude: Number(lng),
        description: description || undefined,
        account_info: accountInfo || undefined,
      });
      setTruck(data as unknown as FoodTruck);
      showToast('가게가 등록되었습니다!', 'success');
    } catch (err: any) {
      showToast(err.response?.data?.detail ?? '등록에 실패했습니다.', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateLocation = async () => {
    if (!truck) return;
    setSaving(true);
    try {
      await truckApi.updateLocation(truck.id, { latitude: Number(lat), longitude: Number(lng) });
      showToast('위치가 업데이트되었습니다.', 'success');
    } catch {
      showToast('위치 업데이트에 실패했습니다.', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleStatus = async () => {
    if (!truck) return;
    setSaving(true);
    try {
      await truckApi.updateStatus(truck.id, !truck.is_open);
      setTruck((prev) => prev ? { ...prev, is_open: !prev.is_open } : prev);
      showToast(`영업 상태가 ${!truck.is_open ? '영업중' : '영업종료'}으로 변경되었습니다.`, 'success');
    } catch {
      showToast('상태 변경에 실패했습니다.', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateMenus = async () => {
    if (editMenus.some((m) => !m.name.trim())) {
      showToast('모든 메뉴명을 입력해주세요.', 'warning');
      return;
    }
    if (!truck) return;
    setMenuSaving(true);
    try {
      await truckApi.updateMenus(truck.id, editMenus.map((m) => ({ name: m.name, price: m.price })));
      setTruck((prev) => prev ? { ...prev, menus: editMenus } : prev);
      showToast('메뉴가 업데이트되었습니다. AI 키워드가 재생성됩니다.', 'success');
    } catch {
      showToast('메뉴 업데이트에 실패했습니다.', 'error');
    } finally {
      setMenuSaving(false);
    }
  };

  const useCurrentLocation = () => {
    requestLocation();
    if (userLocation) {
      setLat(String(userLocation.lat));
      setLng(String(userLocation.lng));
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="manage-page">
      <h2>{truck ? '내 가게 관리' : '가게 등록'}</h2>

      {truck ? (
        <div className="manage-edit">
          <div className="manage-status">
            <p>현재 상태: <strong className={truck.is_open ? 'text-open' : 'text-closed'}>
              {truck.is_open ? '영업중' : '영업종료'}
            </strong></p>
            <Button onClick={handleToggleStatus} variant={truck.is_open ? 'danger' : 'primary'} disabled={saving}>
              {truck.is_open ? '영업 종료' : '영업 시작'}
            </Button>
          </div>

          <div className="manage-location">
            <h3>위치 업데이트</h3>
            <LocationPickerMap
              lat={lat}
              lng={lng}
              onChange={(newLat, newLng) => { setLat(newLat); setLng(newLng); }}
            />
            <Button variant="secondary" onClick={useCurrentLocation}>📍 현재 위치로 이동</Button>
            <Button onClick={handleUpdateLocation} disabled={saving}>위치 저장</Button>
          </div>

          <div className="manage-menus">
            <h3>메뉴 관리</h3>
            <MenuInputList menus={editMenus} onChange={setEditMenus} />
            <Button onClick={handleUpdateMenus} disabled={menuSaving}>
              {menuSaving ? '저장 중...' : '메뉴 저장'}
            </Button>
          </div>
        </div>
      ) : (
        <form className="manage-form" onSubmit={handleCreate}>
          <Input label="가게 이름 *" value={name} onChange={(e) => setName(e.target.value)} required />
          <Input label="소개글" value={description} onChange={(e) => setDescription(e.target.value)} />
          <Input label="계좌 정보" value={accountInfo} onChange={(e) => setAccountInfo(e.target.value)} placeholder="예: 카카오뱅크 1234-5678" />

          <div className="input-group">
            <label className="input-label">위치 *</label>
            <LocationPickerMap
              lat={lat}
              lng={lng}
              onChange={(newLat, newLng) => { setLat(newLat); setLng(newLng); }}
            />
            <button type="button" className="btn btn--secondary" onClick={useCurrentLocation}>📍 현재 위치로 이동</button>
          </div>

          <div className="input-group">
            <label className="input-label">메뉴 *</label>
            <MenuInputList menus={menus} onChange={setMenus} />
          </div>

          <Button type="submit" fullWidth disabled={saving}>
            {saving ? '등록 중...' : '가게 등록'}
          </Button>
        </form>
      )}
    </div>
  );
};

export default TruckManagePage;
