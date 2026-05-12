import type { Menu } from '../../types/truck';

interface Props {
  menus: Menu[];
  onChange: (menus: Menu[]) => void;
}

export const MenuInputList = ({ menus, onChange }: Props) => {
  const addMenu = () => onChange([...menus, { name: '', price: 0 }]);
  const removeMenu = (i: number) => onChange(menus.filter((_, idx) => idx !== i));
  const updateMenu = (i: number, field: keyof Menu, value: string | number) => {
    const updated = [...menus];
    updated[i] = { ...updated[i], [field]: value };
    onChange(updated);
  };

  return (
    <div className="menu-input-list">
      {menus.map((menu, i) => (
        <div key={i} className="menu-row">
          <input
            className="input"
            placeholder="메뉴명"
            value={menu.name}
            onChange={(e) => updateMenu(i, 'name', e.target.value)}
          />
          <input
            className="input input--price"
            type="number"
            placeholder="가격"
            value={menu.price}
            onChange={(e) => updateMenu(i, 'price', Number(e.target.value))}
          />
          <button type="button" className="btn btn--danger btn--sm" onClick={() => removeMenu(i)}>삭제</button>
        </div>
      ))}
      <button type="button" className="btn btn--secondary" onClick={addMenu}>+ 메뉴 추가</button>
    </div>
  );
};
