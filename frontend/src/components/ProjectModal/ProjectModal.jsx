import { useEffect, useState } from 'react';
import './ProjectModal.css';

const defaultFormState = {
  name: '',
  description: ''
};

export default function ProjectModal({
  isOpen,
  mode = 'create',
  initialValues = defaultFormState,
  onClose,
  onSubmit
}) {
  const [formData, setFormData] = useState(defaultFormState);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isOpen) return;

    setFormData({
      name: initialValues?.name || '',
      description: initialValues?.description || ''
    });
    setError('');
  }, [isOpen, initialValues]);

  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const isEditMode = mode === 'edit';
  const modalTitle = isEditMode ? 'Редактировать проект' : 'Создать проект';
  const submitButtonText = isEditMode ? 'Сохранить изменения' : 'Создать проект';

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));

    if (error) {
      setError('');
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    const trimmedName = formData.name.trim();
    const trimmedDescription = formData.description.trim();

    if (!trimmedName) {
      setError('Введите название проекта.');
      return;
    }

    onSubmit({
      name: trimmedName,
      description: trimmedDescription
    });
  };

  return (
    <div className="project-modal-overlay" onClick={onClose}>
      <div
        className="project-modal"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={modalTitle}
      >
        <div className="project-modal__header">
          <h2 className="project-modal__title">{modalTitle}</h2>
          <button
            type="button"
            className="project-modal__close"
            aria-label="Закрыть окно"
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <form className="project-modal__form" onSubmit={handleSubmit}>
          <div className="project-modal__field">
            <label htmlFor="project-name" className="project-modal__label">
              Название проекта <span className="project-modal__required">*</span>
            </label>
            <input
              id="project-name"
              name="name"
              type="text"
              placeholder="Введите название проекта"
              value={formData.name}
              onChange={handleChange}
              className={`project-modal__input ${error ? 'project-modal__input--error' : ''}`}
            />
          </div>

          <div className="project-modal__field">
            <label htmlFor="project-description" className="project-modal__label">
              Описание
            </label>
            <textarea
              id="project-description"
              name="description"
              rows="5"
              placeholder="Введите описание проекта"
              value={formData.description}
              onChange={handleChange}
              className="project-modal__textarea"
            />
          </div>

          {error && <div className="project-modal__error">{error}</div>}

          <div className="project-modal__actions">
            <button
              type="button"
              className="project-modal__button project-modal__button--secondary"
              onClick={onClose}
            >
              Отмена
            </button>
            <button type="submit" className="project-modal__button project-modal__button--primary">
              {submitButtonText}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}