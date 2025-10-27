const select = (selector, scope = document) => scope.querySelector(selector);
const selectAll = (selector, scope = document) => scope.querySelectorAll(selector);

const appShell = select('.pwa-shell');
const drawer = select('.drawer');
const toggle = select('.menu-toggle');
const navLinks = [...selectAll('[data-nav]')];
const sections = [...selectAll('main .section')];
const bottomNav = select('.bottom-nav');
const form = select('.contact-form');
const statusMessage = select('.form-status');
const counters = [...selectAll('[data-counter]')];
const voiceButton = select('[data-voice]');
const voiceStatus = select('[data-voice-status]');
const feedList = select('[data-feed]');
const feedRefresh = select('[data-feed-refresh]');
const screenButtons = [...selectAll('[data-screen]')];
const screenPanels = [...selectAll('[data-screen-panel]')];

const closeDrawer = () => {
  drawer?.classList.remove('open');
  drawer?.setAttribute('aria-hidden', 'true');
  toggle?.setAttribute('aria-expanded', 'false');
  appShell?.classList.remove('drawer-open');
};

const openDrawer = () => {
  drawer?.classList.add('open');
  drawer?.setAttribute('aria-hidden', 'false');
  toggle?.setAttribute('aria-expanded', 'true');
  appShell?.classList.add('drawer-open');
};

toggle?.addEventListener('click', () => {
  if (drawer?.classList.contains('open')) {
    closeDrawer();
  } else {
    openDrawer();
  }
});

navLinks.forEach(link => {
  link.addEventListener('click', () => closeDrawer());
});

const animateElements = () => {
  if (!('IntersectionObserver' in window)) {
    selectAll('[data-animate]').forEach(element => element.classList.add('in-view'));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.2 });

  selectAll('[data-animate]').forEach(element => observer.observe(element));
};

animateElements();

const formatCounterValue = (value, decimals, prefix = '', suffix = '') => {
  const factor = 10 ** decimals;
  const formatted = decimals ? Math.round(value * factor) / factor : Math.round(value);
  return `${prefix}${formatted.toLocaleString('es-ES')}${suffix}`;
};

const animateCounter = (element) => {
  if (element.dataset.animated === 'true') return;
  const target = Number(element.dataset.counter ?? element.textContent ?? '0');
  if (Number.isNaN(target)) return;
  const prefix = element.dataset.prefix ?? '';
  const suffix = element.dataset.suffix ?? '';
  const decimals = Number(element.dataset.decimals ?? '0');
  const duration = Number(element.dataset.duration ?? '1400');
  const startValue = Number(element.dataset.start ?? '0');
  const startTime = performance.now();

  const step = (now) => {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = startValue + (target - startValue) * eased;
    element.textContent = formatCounterValue(current, decimals, prefix, suffix);
    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      element.textContent = formatCounterValue(target, decimals, prefix, suffix);
    }
  };

  element.dataset.animated = 'true';
  requestAnimationFrame(step);
};

if ('IntersectionObserver' in window) {
  const counterObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.6 });

  counters.forEach(counter => counterObserver.observe(counter));
} else {
  counters.forEach(counter => animateCounter(counter));
}

const activateNav = (id) => {
  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    const isActive = href === `#${id}`;
    link.classList.toggle('active', isActive);
  });
};

const getActiveSection = () => {
  let current = sections[0]?.id ?? '';
  const offset = window.innerHeight * 0.24;
  sections.forEach(section => {
    const rect = section.getBoundingClientRect();
    if (rect.top - offset <= 0 && rect.bottom - offset > 0) {
      current = section.id;
    }
  });
  return current;
};

const onScroll = () => {
  const activeId = getActiveSection();
  if (activeId) activateNav(activeId);
};

document.addEventListener('scroll', onScroll, { passive: true });
window.addEventListener('resize', onScroll);
window.addEventListener('load', onScroll);

const validators = {
  nombre: value => value.trim().length >= 3 || 'Ingresa tu nombre completo.',
  correo: value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Introduce un correo válido.',
  telefono: value => /^[+0-9\s-]{8,}$/.test(value) || 'Añade un teléfono de contacto válido.',
  empresa: value => value.trim().length >= 2 || 'Especifica tu empresa o marca.',
  interes: value => value.trim().length > 0 || 'Selecciona un interés principal.',
  mensaje: value => value.trim().length >= 12 || 'Cuéntanos más sobre tu proyecto.'
};

const showError = (input, message) => {
  const field = input.closest('.form-group');
  const error = field?.querySelector('.error');
  if (!error) return;
  if (message) {
    field?.classList.add('has-error');
    error.textContent = message;
  } else {
    field?.classList.remove('has-error');
    error.textContent = '';
  }
};

const validateField = (input) => {
  const name = input.name;
  if (!name || !validators[name]) return true;
  const result = validators[name](input.value);
  const isValid = result === true;
  showError(input, isValid ? '' : result);
  return isValid;
};

form?.addEventListener('input', (event) => {
  const target = event.target;
  if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement) {
    validateField(target);
  }
});

form?.addEventListener('submit', (event) => {
  event.preventDefault();
  if (!form) return;

  const inputs = [...form.elements].filter(el => el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement || el instanceof HTMLSelectElement);
  const results = inputs.map(input => validateField(input));
  const isValid = results.every(Boolean);

  if (!isValid) {
    if (statusMessage) {
      statusMessage.textContent = 'Revisa los campos marcados para continuar.';
      statusMessage.classList.remove('success');
      statusMessage.classList.add('error');
    }
    return;
  }

  if (statusMessage) {
    statusMessage.textContent = 'Gracias por tu interés. Nuestro equipo te contactará en menos de 24 horas.';
    statusMessage.classList.remove('error');
    statusMessage.classList.add('success');
  }

  form.reset();
  inputs.forEach(input => showError(input, ''));
});

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./service-worker.js').catch(() => {
      // registro silencioso
    });
  });
}

bottomNav?.addEventListener('click', (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;
  const link = target.closest('a');
  if (!link) return;
  bottomNav.classList.add('active');
  setTimeout(() => bottomNav.classList.remove('active'), 600);
});

let voiceTimeout;
let voiceResetTimeout;
voiceButton?.addEventListener('click', () => {
  if (!voiceButton || !voiceStatus) return;
  voiceButton.classList.add('active');
  voiceButton.setAttribute('aria-pressed', 'true');
  voiceStatus.textContent = 'Aurvo Voice Pilot: escuchando tu comando…';
  clearTimeout(voiceTimeout);
  clearTimeout(voiceResetTimeout);
  voiceTimeout = window.setTimeout(() => {
    voiceButton.classList.remove('active');
    voiceButton.setAttribute('aria-pressed', 'false');
    voiceStatus.textContent = 'Comando ejecutado · Showroom nocturno desplegado.';
    voiceResetTimeout = window.setTimeout(() => {
      voiceStatus.textContent = 'Escucha pasiva · listo para recibir órdenes';
    }, 3200);
  }, 2000);
});

const feedUpdates = [
  { time: '09:49', message: 'Voice Pilot activó streaming 8K en Ginebra.' },
  { time: '09:46', message: 'Analytics Edge elevó puja premium en Hong Kong (+17%).' },
  { time: '09:44', message: 'Concierge infinito confirmó cita privada en Dubái.' },
  { time: '09:42', message: 'Reality Suite sincronizó iluminación en pista nocturna.' }
];

let feedIndex = 0;
feedRefresh?.addEventListener('click', () => {
  if (!feedList) return;
  const update = feedUpdates[feedIndex % feedUpdates.length];
  feedIndex += 1;

  const item = document.createElement('li');
  const time = document.createElement('time');
  time.dateTime = update.time;
  time.textContent = update.time;
  const paragraph = document.createElement('p');
  paragraph.textContent = update.message;
  item.append(time, paragraph);
  item.classList.add('injected');
  feedList.prepend(item);

  while (feedList.children.length > 5) {
    const last = feedList.lastElementChild;
    if (last) feedList.removeChild(last);
  }
});

const activateScreen = (targetId) => {
  screenButtons.forEach(button => {
    const isActive = button.dataset.screen === targetId;
    button.classList.toggle('active', isActive);
    button.setAttribute('aria-selected', String(isActive));
    button.setAttribute('tabindex', isActive ? '0' : '-1');
  });

  screenPanels.forEach(panel => {
    const isActive = panel.dataset.screenPanel === targetId;
    panel.classList.toggle('active', isActive);
    panel.hidden = !isActive;
  });
};

screenButtons.forEach(button => {
  button.addEventListener('click', () => {
    const targetId = button.dataset.screen;
    if (!targetId) return;
    activateScreen(targetId);
  });

  button.addEventListener('keydown', (event) => {
    if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
    event.preventDefault();
    const direction = event.key === 'ArrowRight' ? 1 : -1;
    const index = screenButtons.indexOf(button);
    const nextIndex = (index + direction + screenButtons.length) % screenButtons.length;
    screenButtons[nextIndex]?.focus();
    const targetId = screenButtons[nextIndex]?.dataset.screen;
    if (targetId) activateScreen(targetId);
  });
});

if (screenButtons.length) {
  const defaultTarget = screenButtons.find(button => button.classList.contains('active'))?.dataset.screen || screenButtons[0]?.dataset.screen;
  if (defaultTarget) activateScreen(defaultTarget);
}

let screenInterval;
const cycleScreens = () => {
  if (!screenButtons.length) return;
  clearInterval(screenInterval);
  screenInterval = window.setInterval(() => {
    const currentIndex = screenButtons.findIndex(button => button.classList.contains('active'));
    const nextIndex = (currentIndex + 1) % screenButtons.length;
    const nextTarget = screenButtons[nextIndex]?.dataset.screen;
    if (nextTarget) activateScreen(nextTarget);
  }, 7000);
};

cycleScreens();

screenButtons.forEach(button => {
  button.addEventListener('click', cycleScreens);
});

onScroll();
