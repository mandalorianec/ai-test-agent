import { NavLink } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';
import './Header.css';

function NotificationIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M12 22a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22Zm7-4H5l1.5-1.8V11a5.5 5.5 0 0 1 4.5-5.41V4.75a1 1 0 1 1 2 0v.84A5.5 5.5 0 0 1 17.5 11v5.2L19 18Z"
        fill="currentColor"
      />
    </svg>
  );
}

function LogoIcon() {
  return (
    <svg viewBox="0 0 32 32" aria-hidden="true">
      <rect x="4" y="4" width="24" height="24" rx="8" fill="currentColor" opacity="0.12" />
      <path
        d="M15 9c0-.83.67-1.5 1.5-1.5S18 8.17 18 9s-.67 1.5-1.5 1.5S15 9.83 15 9Zm-3 5.25c0-.69.56-1.25 1.25-1.25h6.5c.69 0 1.25.56 1.25 1.25s-.56 1.25-1.25 1.25H17.5V23a1.5 1.5 0 0 1-3 0v-7.5h-1.25c-.69 0-1.25-.56-1.25-1.25Z"
        fill="currentColor"
      />
    </svg>
  );
}

function UserAvatarIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2.24-8 5v1h16v-1c0-2.76-3.58-5-8-5Z"
        fill="currentColor"
      />
    </svg>
  );
}

export default function Header() {
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setIsUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <div className="site-header__left">
          <a href="/projects" className="site-logo">
            <span className="site-logo__icon">
              <LogoIcon />
            </span>
            <span className="site-logo__text">AI Test Agent</span>
          </a>
        </div>

        <nav className="site-header__center">
          <NavLink
            to="/projects"
            className={({ isActive }) =>
              isActive ? 'site-nav__link site-nav__link--active' : 'site-nav__link'
            }
          >
            Проекты
          </NavLink>
        </nav>

        <div className="site-header__right">
          <button className="header-icon-button" type="button" aria-label="Уведомления">
            <NotificationIcon />
          </button>

          <div className="user-menu" ref={userMenuRef}>
            <button
              className="header-avatar-button"
              type="button"
              aria-label="Меню пользователя"
              onClick={() => setIsUserMenuOpen((prev) => !prev)}
            >
              <UserAvatarIcon />
            </button>

            {isUserMenuOpen && (
              <div className="user-menu__dropdown">
                <button type="button" className="user-menu__item">
                  Профиль
                </button>
                <button type="button" className="user-menu__item">
                  Редактировать профиль
                </button>
                <button type="button" className="user-menu__item user-menu__item--danger">
                  Выход
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}