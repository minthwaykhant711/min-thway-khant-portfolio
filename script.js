const menuBtn = document.querySelector('.menu-btn');
const navLinks = document.querySelector('.nav-links');

function closeNavigation() {
  navLinks?.classList.remove('open');
  menuBtn?.setAttribute('aria-expanded', 'false');
  menuBtn?.setAttribute('aria-label', 'Open navigation');
}

menuBtn?.addEventListener('click', () => {
  const open = navLinks?.classList.toggle('open') ?? false;
  menuBtn.setAttribute('aria-expanded', String(open));
  menuBtn.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
});

document.querySelectorAll('.nav-links a').forEach((link) => {
  link.addEventListener('click', closeNavigation);
});

document.addEventListener('click', (event) => {
  if (!navLinks?.classList.contains('open')) return;
  if (navLinks.contains(event.target) || menuBtn?.contains(event.target)) return;
  closeNavigation();
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') closeNavigation();
});

window.addEventListener('resize', () => {
  if (window.innerWidth > 900) closeNavigation();
});

// Add future project media by adding filenames to that project's media array.
const projects = {
  room: {
    title: 'Room Reservation System',
    kicker: 'TEAM PROJECT · ROOM RESERVATION',
    description: 'A reservation platform for study, multimedia and meeting rooms, with booking requests, approval workflows, booking history and staff-side room management.',
    role: 'Team Leader / Project Manager & Developer',
    images: [
      'assets/projects/roomreservation/login.png',
      'assets/projects/roomreservation/room-management.png',
      'assets/projects/roomreservation/room-booking-history.png',
      'assets/projects/roomreservation/room-requests.png',
      'assets/projects/roomreservation/room-add.png'
    ]
  },
  asset: {
    title: 'Asset Borrowing System',
    kicker: 'TEAM PROJECT · WEB SYSTEM',
    description: 'A role-based asset borrowing system covering browsing, borrowing requests, approval workflows, returned-asset records and history for students, lecturers and staff.',
    role: 'Team Leader / Project Manager & Developer',
    images: [
      'assets/projects/assetmanage/asset-login.png',
      'assets/projects/assetmanage/asset-register.png',
      'assets/projects/assetmanage/asset-browse.png',
      'assets/projects/assetmanage/asset-details.png',
      'assets/projects/assetmanage/asset-staff.png',
      'assets/projects/assetmanage/asset-return.png',
      'assets/projects/assetmanage/asset-history.png',
      
    ]
  },
  elearning: {
    title: 'HCIA Datacom E-Learning Platform',
    kicker: '2026 — PRESENT · SENIOR PROJECT',
    description: 'A team-built learning platform designed for networking students, combining structured learning modules, quizzes, mock tests and practical networking lab tutorials.',
    role: 'Team Leader / Project Manager & Developer',
    images: [
      'assets/projects/hcia-elearning/welcome.png',
      'assets/projects/hcia-elearning/login.png',
      'assets/projects/hcia-elearning/register.png',
      'assets/projects/hcia-elearning/enroll.png',
      'assets/projects/hcia-elearning/student_dashboard.png',
      'assets/projects/hcia-elearning/student_learning.png',
      'assets/projects/hcia-elearning/student_quiz.png',
      'assets/projects/hcia-elearning/student_mock.png'
    ]
  },
  hugmae: {
    title: 'Offline-First Rural Healthcare Application',
    kicker: '2025 — 2026 · HUGMAE HACKATHON',
    description: 'An AI-powered offline-first healthcare concept designed to improve access to healthcare services in underserved and rural communities.',
    role: 'Team Leader / Project Manager & Solution Contributor',
    videos: [
      'assets/projects/hugmae/sync-medgo.mp4',
      'assets/projects/hugmae/scan-patient-medgo.mp4',
      'assets/projects/hugmae/new-consultation-medgo.mp4'
    ]
  }
};

const modal = document.getElementById('projectModal');
const modalImage = document.getElementById('modalImage');
const modalVideo = document.getElementById('modalVideo');
const modalTitle = document.getElementById('modalTitle');
const modalKicker = document.getElementById('modalKicker');
const modalDescription = document.getElementById('modalDescription');
const modalRole = document.getElementById('modalRole');
const modalCounter = document.getElementById('modalCounter');
let currentProject = null;
let currentImage = 0;

function showImage() {
  const project = projects[currentProject];
  const media = project.videos || project.images;
  const src = media[currentImage];
  const isVideo = /\.mp4$/i.test(src);
  modalVideo.pause();
  modalVideo.removeAttribute('src');
  modalVideo.load();
  modalVideo.currentTime = 0;
  modalImage.hidden = isVideo;
  modalVideo.hidden = !isVideo;
  if (isVideo) {
    modalVideo.src = src;
    modalVideo.load();
    modalVideo.currentTime = 0;
  } else {
    modalImage.src = src;
    modalImage.alt = `${project.title} screenshot ${currentImage + 1}`;
  }
  modalCounter.textContent = `${currentImage + 1} / ${media.length}`;
}

function openProject(key) {
  const project = projects[key];
  if (!project) return;
  currentProject = key;
  currentImage = 0;
  modalTitle.textContent = project.title;
  modalKicker.textContent = project.kicker;
  modalDescription.textContent = project.description;
  modalRole.textContent = `MY ROLE · ${project.role}`;
  showImage();
  modal.classList.add('open');
  modal.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}

function closeProject() {
  modalVideo.pause();
  modal.classList.remove('open');
  modal.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

document.querySelectorAll('[data-project]').forEach((card) => {
  card.querySelector('.clean-project-image')?.addEventListener('click', () => openProject(card.dataset.project));
  card.querySelector('.no-image-header')?.addEventListener('click', () => openProject(card.dataset.project));
  card.querySelector('.view-project-btn')?.addEventListener('click', () => openProject(card.dataset.project));
});

document.querySelectorAll('[data-close]').forEach((element) => {
  element.addEventListener('click', closeProject);
});

document.querySelector('.gallery-prev')?.addEventListener('click', () => {
  if (!currentProject) return;
  const media = projects[currentProject].videos || projects[currentProject].images;
  const total = media.length;
  currentImage = (currentImage - 1 + total) % total;
  showImage();
});

document.querySelector('.gallery-next')?.addEventListener('click', () => {
  if (!currentProject) return;
  const media = projects[currentProject].videos || projects[currentProject].images;
  currentImage = (currentImage + 1) % media.length;
  showImage();
});

document.addEventListener('keydown', (event) => {
  if (!modal.classList.contains('open')) return;
  if (event.key === 'Escape') closeProject();
  if (event.key === 'ArrowLeft') document.querySelector('.gallery-prev')?.click();
  if (event.key === 'ArrowRight') document.querySelector('.gallery-next')?.click();
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) entry.target.classList.add('visible');
  });
}, { threshold: 0.08 });

document.querySelectorAll('.clean-project-card,.skill-group,.timeline article,.credential').forEach((element) => {
  element.style.opacity = '0';
  element.style.transform = 'translateY(18px)';
  element.style.transition = 'opacity .55s ease, transform .55s ease';
  observer.observe(element);
});
