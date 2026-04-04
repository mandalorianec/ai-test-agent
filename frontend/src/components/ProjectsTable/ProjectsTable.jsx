import { useNavigate } from 'react-router-dom';
import './ProjectsTable.css';

export default function ProjectsTable({ projects, onEdit }) {
  const navigate = useNavigate();

  const handleRowClick = (projectId) => {
    navigate(`/projects/${projectId}`);
  };

  if (!projects.length) {
    return (
      <div className="projects-empty-state">
        <h3 className="projects-empty-state__title">Проектов пока нет</h3>
        <p className="projects-empty-state__text">
          Создайте первый проект, чтобы он появился в списке.
        </p>
      </div>
    );
  }

  return (
    <div className="projects-table-wrapper">
      <table className="projects-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Название проекта</th>
            <th>Описание</th>
            <th>Тест-кейсы</th>
            <th>Действия</th>
          </tr>
        </thead>

        <tbody>
          {projects.map((project) => (
            <tr
              key={project.id}
              className="projects-table__row"
              onClick={() => handleRowClick(project.id)}
            >
              <td className="projects-table__id">{project.id}</td>
              <td className="projects-table__name">{project.name}</td>
              <td className="projects-table__description">{project.description || '—'}</td>
              <td className="projects-table__count">{project.testCasesCount}</td>
              <td className="projects-table__actions">
                <button
                  type="button"
                  className="projects-table__edit-button"
                  onClick={(event) => {
                    event.stopPropagation();
                    onEdit(project);
                  }}
                >
                  Редактировать
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}