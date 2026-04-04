import { Link, useParams } from 'react-router-dom';

export default function ProjectDetails({ projects }) {
  const { id } = useParams();

  const project = projects.find((item) => String(item.id) === String(id));

  if (!project) {
    return (
      <section
        style={{
          background: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '18px',
          padding: '32px'
        }}
      >
        <h1 style={{ marginTop: 0 }}>Проект не найден</h1>
        <p style={{ color: '#6b7280' }}>
          Проект с таким идентификатором отсутствует.
        </p>
        <Link
          to="/projects"
          style={{
            display: 'inline-flex',
            marginTop: '16px',
            padding: '12px 18px',
            borderRadius: '12px',
            background: '#2563eb',
            color: '#ffffff',
            fontWeight: 600
          }}
        >
          Вернуться к проектам
        </Link>
      </section>
    );
  }

  return (
    <section
      style={{
        background: '#ffffff',
        border: '1px solid #e5e7eb',
        borderRadius: '18px',
        padding: '32px',
        boxShadow: '0 10px 30px rgba(15, 23, 42, 0.04)'
      }}
    >
      <div style={{ marginBottom: '24px' }}>
        <Link
          to="/projects"
          style={{
            color: '#2563eb',
            fontWeight: 600
          }}
        >
          ← Назад к проектам
        </Link>
      </div>

      <h1 style={{ marginTop: 0, marginBottom: '12px' }}>{project.name}</h1>

      <p style={{ marginTop: 0, marginBottom: '20px', color: '#4b5563', fontSize: '16px' }}>
        {project.description || 'Описание пока не добавлено.'}
      </p>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '16px'
        }}
      >
        <div
          style={{
            padding: '18px',
            borderRadius: '16px',
            background: '#f9fafb',
            border: '1px solid #eef2f7'
          }}
        >
          <div style={{ color: '#6b7280', marginBottom: '8px' }}>ID проекта</div>
          <div style={{ fontSize: '20px', fontWeight: 700 }}>{project.id}</div>
        </div>

        <div
          style={{
            padding: '18px',
            borderRadius: '16px',
            background: '#f9fafb',
            border: '1px solid #eef2f7'
          }}
        >
          <div style={{ color: '#6b7280', marginBottom: '8px' }}>Тест-кейсы</div>
          <div style={{ fontSize: '20px', fontWeight: 700 }}>{project.testCasesCount}</div>
        </div>
      </div>

      <div
        style={{
          marginTop: '28px',
          padding: '20px',
          borderRadius: '16px',
          background: '#eef4ff',
          color: '#1e40af',
          fontWeight: 500
        }}
      >
        Это временная страница проекта. Основной интерфейс проекта можно будет добавить следующим этапом.
      </div>
    </section>
  );
}