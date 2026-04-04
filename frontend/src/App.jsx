import { useEffect, useState } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import Header from './components/Header/Header';
import ProjectsPage from './pages/ProjectsPage';
import ProjectDetails from './pages/ProjectDetails';
import { initialProjects } from './data/mockProjects';

const STORAGE_KEY = 'ai-test-agent-projects';

function App() {
  const [projects, setProjects] = useState(() => {
    const savedProjects = localStorage.getItem(STORAGE_KEY);

    if (savedProjects) {
      try {
        return JSON.parse(savedProjects);
      } catch (error) {
        console.error('Ошибка чтения проектов из localStorage:', error);
      }
    }

    return initialProjects;
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
  }, [projects]);

  const handleCreateProject = ({ name, description }) => {
    const nextId =
      projects.length > 0
        ? Math.max(...projects.map((project) => Number(project.id))) + 1
        : 1;

    const newProject = {
      id: nextId,
      name,
      description,
      testCasesCount: 0
    };

    setProjects((prevProjects) => [newProject, ...prevProjects]);
  };

  const handleEditProject = (updatedProject) => {
    setProjects((prevProjects) =>
      prevProjects.map((project) =>
        project.id === updatedProject.id ? { ...project, ...updatedProject } : project
      )
    );
  };

  return (
    <div className="app-shell">
      <Header />

      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/projects" replace />} />
          <Route
            path="/projects"
            element={
              <ProjectsPage
                projects={projects}
                onCreateProject={handleCreateProject}
                onEditProject={handleEditProject}
              />
            }
          />
          <Route
            path="/projects/:id"
            element={<ProjectDetails projects={projects} />}
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;