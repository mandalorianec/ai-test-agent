import { useState } from 'react';
import ProjectModal from '../components/ProjectModal/ProjectModal';
import ProjectsTable from '../components/ProjectsTable/ProjectsTable';
import './ProjectsPage.css';

export default function ProjectsPage({ projects, onCreateProject, onEditProject }) {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState(null);

  const closeCreateModal = () => {
    setIsCreateModalOpen(false);
  };

  const closeEditModal = () => {
    setEditingProject(null);
  };

  const handleCreateSubmit = (formData) => {
    onCreateProject(formData);
    closeCreateModal();
  };

  const handleEditSubmit = (formData) => {
    onEditProject({
      ...editingProject,
      ...formData
    });
    closeEditModal();
  };

  return (
    <section className="projects-page">
      <div className="projects-page__topbar">
        <button
          type="button"
          className="projects-page__create-button"
          onClick={() => setIsCreateModalOpen(true)}
        >
          Создать проект
        </button>
      </div>

      <ProjectsTable
        projects={projects}
        onEdit={(project) => {
          setEditingProject(project);
        }}
      />

      <ProjectModal
        isOpen={isCreateModalOpen}
        mode="create"
        onClose={closeCreateModal}
        onSubmit={handleCreateSubmit}
      />

      <ProjectModal
        isOpen={Boolean(editingProject)}
        mode="edit"
        initialValues={editingProject}
        onClose={closeEditModal}
        onSubmit={handleEditSubmit}
      />
    </section>
  );
}