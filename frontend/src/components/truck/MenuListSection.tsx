import type { Menu } from '../../types/truck';

interface Props {
  menus: Menu[];
}

export const MenuListSection = ({ menus }: Props) => (
  <div className="menu-section">
    <h3 className="section-title">메뉴</h3>
    {menus.length === 0 ? (
      <p className="empty-message">등록된 메뉴가 없습니다.</p>
    ) : (
      <ul className="menu-list">
        {menus.map((m, i) => (
          <li key={m.id ?? i} className="menu-item">
            <span className="menu-item__name">{m.name}</span>
            <span className="menu-item__price">{m.price.toLocaleString()}원</span>
          </li>
        ))}
      </ul>
    )}
  </div>
);
