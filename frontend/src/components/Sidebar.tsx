import React from 'react';

interface SidebarProps {
  activePage: string;
  onPageChange: (page: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activePage, onPageChange }) => {
  const menuItems = [
    { id: 'dashboard', label: '仪表盘概览', icon: '🏠' },
    { id: 'passenger-flow', label: '客流分析', icon: '📊' },
    { id: 'temporal-trend', label: '时间趋势', icon: '⏰' },
    { id: 'spatial-distribution', label: '空间分布', icon: '🗺️' },
    { id: 'line-optimization', label: '线路优化', icon: '📈' },
    { id: 'station-metrics', label: '站点指标', icon: '🚆' },
    { id: 'data-management', label: '数据管理', icon: '💾' },
    { id: 'settings', label: '系统设置', icon: '⚙️' },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <span className="logo-icon">🚆</span>
          <h2>铁路运营分析</h2>
        </div>
        <div className="system-status">
          <div className="status-indicator active"></div>
          <span>系统在线</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <ul>
          {menuItems.map((item) => (
            <li key={item.id}>
              <button
                className={`nav-button ${activePage === item.id ? 'active' : ''}`}
                onClick={() => onPageChange(item.id)}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
                {activePage === item.id && <div className="active-indicator"></div>}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-footer">
        <div className="user-info">
          <div className="user-avatar">
            <span>管理员</span>
          </div>
          <div className="user-details">
            <p className="user-name">系统管理员</p>
            <p className="user-role">高级权限</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;