/**
 * Resume Tailor Pro - Frontend Client Application
 * Vanilla JavaScript implementation for AJAX generation, progressive steps,
 * character counting, validation, and localStorage history management.
 */

(function() {
  'use strict';

  // DOM Elements Cache
  const form = document.getElementById('resume-form');
  const companyInput = document.getElementById('company');
  const countrySelect = document.getElementById('country');
  const jdTextarea = document.getElementById('jd');
  const jdCounter = document.getElementById('jd-counter');
  const generateBtn = document.getElementById('generate-btn');
  const btnText = generateBtn ? generateBtn.querySelector('.btn-text') : null;

  const loadingCard = document.getElementById('loading-card');
  const successCard = document.getElementById('success-card');
  const errorCard = document.getElementById('error-card');
  const errorMessage = document.getElementById('error-message');

  const resFilename = document.getElementById('res-filename');
  const resPath = document.getElementById('res-path');
  const successMessage = document.getElementById('success-message');
  const downloadBtn = document.getElementById('download-btn');
  const copyPathBtn = document.getElementById('copy-path-btn');
  const newResumeBtn = document.getElementById('new-resume-btn');
  const errorRetryBtn = document.getElementById('error-retry-btn');

  const generationTimer = document.getElementById('generation-timer');
  const historyList = document.getElementById('history-list');
  const historyCount = document.getElementById('history-count');
  const clearHistoryBtn = document.getElementById('clear-history-btn');

  const stepItems = [
    document.getElementById('step-1'),
    document.getElementById('step-2'),
    document.getElementById('step-3'),
    document.getElementById('step-4')
  ];

  const STORAGE_KEY = 'resume_tailor_pro_history';
  let timerInterval = null;
  let stepInterval = null;
  let startTime = null;

  // ----------------------------------------------------
  // Quick Chip Company Fill
  // ----------------------------------------------------
  document.querySelectorAll('.chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const company = btn.getAttribute('data-company');
      if (company && companyInput) {
        companyInput.value = company;
        companyInput.focus();
      }
    });
  });

  // ----------------------------------------------------
  // Job Description Real-time Character & Word Counter
  // ----------------------------------------------------
  function updateJdCounter() {
    if (!jdTextarea || !jdCounter) return;
    const text = jdTextarea.value.trim();
    const charCount = jdTextarea.value.length;
    const words = text ? text.split(/\s+/).length : 0;
    
    jdCounter.textContent = `${charCount.toLocaleString()} chars • ~${words.toLocaleString()} words`;
    
    if (charCount >= 80) {
      jdCounter.classList.add('counter-valid');
    } else {
      jdCounter.classList.remove('counter-valid');
    }
  }

  if (jdTextarea) {
    jdTextarea.addEventListener('input', updateJdCounter);
    updateJdCounter();
  }

  // ----------------------------------------------------
  // Step Animation & Progress Sequencer
  // ----------------------------------------------------
  function resetProgressSteps() {
    stepItems.forEach((step, idx) => {
      if (!step) return;
      step.classList.remove('is-active', 'is-complete');
      if (idx === 0) {
        step.classList.add('is-active');
      }
    });
  }

  function startProgressAnimation() {
    resetProgressSteps();
    startTime = Date.now();
    if (generationTimer) generationTimer.textContent = '00:00s';

    // Timer interval
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      if (!generationTimer) return;
      const elapsedSec = Math.floor((Date.now() - startTime) / 1000);
      const formatted = String(elapsedSec).padStart(2, '0');
      generationTimer.textContent = `00:${formatted}s`;
    }, 1000);

    // Realistic progressive step transitions
    let currentStep = 0;
    clearInterval(stepInterval);
    stepInterval = setInterval(() => {
      if (currentStep < 3) {
        if (stepItems[currentStep]) {
          stepItems[currentStep].classList.remove('is-active');
          stepItems[currentStep].classList.add('is-complete');
        }
        currentStep++;
        if (stepItems[currentStep]) {
          stepItems[currentStep].classList.add('is-active');
        }
      }
    }, 2800);
  }

  function completeProgressAnimation() {
    clearInterval(timerInterval);
    clearInterval(stepInterval);
    stepItems.forEach(step => {
      if (step) {
        step.classList.remove('is-active');
        step.classList.add('is-complete');
      }
    });
  }

  function stopProgressAnimation() {
    clearInterval(timerInterval);
    clearInterval(stepInterval);
  }

  // ----------------------------------------------------
  // UI State Management
  // ----------------------------------------------------
  function setLoadingState(isLoading) {
    if (!generateBtn || !loadingCard) return;

    if (isLoading) {
      generateBtn.disabled = true;
      generateBtn.classList.add('is-loading');
      if (btnText) btnText.textContent = 'Tailoring Resume...';

      loadingCard.classList.add('active');
      if (successCard) successCard.classList.remove('active');
      if (errorCard) errorCard.classList.remove('active');

      startProgressAnimation();

      if (window.innerWidth <= 1024) {
        loadingCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    } else {
      generateBtn.disabled = false;
      generateBtn.classList.remove('is-loading');
      if (btnText) btnText.textContent = 'Generate ATS-Optimized Resume';
      stopProgressAnimation();
      loadingCard.classList.remove('active');
    }
  }

  function showSuccess(data) {
    completeProgressAnimation();
    
    setTimeout(() => {
      if (loadingCard) loadingCard.classList.remove('active');
      if (errorCard) errorCard.classList.remove('active');
      if (successCard) successCard.classList.add('active');

      if (resFilename) resFilename.textContent = data.filename || 'Tailored_Resume.pdf';
      if (resPath) resPath.textContent = data.pdf_path || 'output/Tailored_Resume.pdf';
      if (data.message && successMessage) {
        successMessage.textContent = data.message;
      }

      const downloadUrl = `/download/${encodeURIComponent(data.filename)}`;
      if (downloadBtn) {
        downloadBtn.setAttribute('href', downloadUrl);
        downloadBtn.setAttribute('download', data.filename || 'Resume.pdf');
      }

      if (window.innerWidth <= 1024 && successCard) {
        successCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 400);
  }

  function showError(messageText) {
    stopProgressAnimation();
    if (loadingCard) loadingCard.classList.remove('active');
    if (successCard) successCard.classList.remove('active');
    if (errorCard) {
      errorCard.classList.add('active');
      if (errorMessage) {
        errorMessage.textContent = messageText || 'Failed to generate resume. Please verify your settings and try again.';
      }
      if (window.innerWidth <= 1024) {
        errorCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  }

  // ----------------------------------------------------
  // Copy Path to Clipboard
  // ----------------------------------------------------
  if (copyPathBtn && resPath) {
    copyPathBtn.addEventListener('click', async () => {
      const pathText = resPath.textContent;
      try {
        await navigator.clipboard.writeText(pathText);
        const origHtml = copyPathBtn.innerHTML;
        copyPathBtn.innerHTML = `
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        `;
        setTimeout(() => {
          copyPathBtn.innerHTML = origHtml;
        }, 2000);
      } catch (err) {
        console.error('Clipboard copy failed:', err);
      }
    });
  }

  if (newResumeBtn) {
    newResumeBtn.addEventListener('click', () => {
      if (successCard) successCard.classList.remove('active');
      if (jdTextarea) {
        jdTextarea.value = '';
        updateJdCounter();
      }
      if (companyInput) companyInput.focus();
    });
  }

  if (errorRetryBtn) {
    errorRetryBtn.addEventListener('click', () => {
      if (errorCard) errorCard.classList.remove('active');
      if (companyInput) companyInput.focus();
    });
  }

  // ----------------------------------------------------
  // LocalStorage History Management
  // ----------------------------------------------------
  function getHistory() {
    try {
      const items = localStorage.getItem(STORAGE_KEY);
      return items ? JSON.parse(items) : [];
    } catch (e) {
      console.error('Failed reading history:', e);
      return [];
    }
  }

  function saveHistoryItem(item) {
    const history = getHistory();
    history.unshift(item);
    const trimmed = history.slice(0, 20);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
    renderHistory();
  }

  function deleteHistoryItem(id) {
    const history = getHistory().filter(item => item.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    renderHistory();
  }

  function clearHistory() {
    if (confirm('Clear all resume generation history?')) {
      localStorage.removeItem(STORAGE_KEY);
      renderHistory();
    }
  }

  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener('click', clearHistory);
  }

  function renderHistory() {
    if (!historyList || !historyCount) return;
    const history = getHistory();
    historyCount.textContent = history.length;
    historyList.innerHTML = '';

    if (history.length === 0) {
      historyList.innerHTML = `
        <li class="history-empty-state">
          <svg class="history-empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          <span class="history-empty-title">No Resumes Generated Yet</span>
          <span class="history-empty-desc">Your tailored resumes will appear here for fast access and download.</span>
        </li>
      `;
      return;
    }

    history.forEach(item => {
      const li = document.createElement('li');
      li.className = 'history-item';

      const timeFormatted = new Date(item.timestamp).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });

      const downloadLink = `/download/${encodeURIComponent(item.filename)}`;

      li.innerHTML = `
        <div class="history-item-left">
          <div class="history-doc-icon">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
          </div>
          <div class="history-item-details">
            <span class="history-item-company">${escapeHtml(item.company)} (${escapeHtml(item.country)})</span>
            <div class="history-item-meta">
              <span class="history-provider-tag">${escapeHtml(item.ai_provider.toUpperCase())}</span>
              <span>&bull;</span>
              <span>${timeFormatted}</span>
            </div>
          </div>
        </div>
        <div class="history-item-actions">
          <a href="${downloadLink}" download="${escapeHtml(item.filename)}" class="btn-history-action" title="Download">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            <span>PDF</span>
          </a>
          <button type="button" class="btn-history-action btn-history-delete" data-id="${item.id}" title="Remove">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      `;

      const delBtn = li.querySelector('.btn-history-delete');
      if (delBtn) {
        delBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          deleteHistoryItem(item.id);
        });
      }

      historyList.appendChild(li);
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // Initial history render
  renderHistory();

  // ----------------------------------------------------
  // Form Submission (AJAX JSON POST to /generate)
  // ----------------------------------------------------
  if (form) {
    form.addEventListener('submit', async function(e) {
      e.preventDefault();

      const company = companyInput ? companyInput.value.trim() : '';
      const country = countrySelect ? countrySelect.value.trim() : '';
      const jd = jdTextarea ? jdTextarea.value.trim() : '';
      const aiProviderRadio = document.querySelector('input[name="ai_provider"]:checked');
      const ai_provider = aiProviderRadio ? aiProviderRadio.value : 'gemini';

      if (!company) {
        showError('Please enter the target Company Name.');
        if (companyInput) companyInput.focus();
        return;
      }

      if (!country) {
        showError('Please select a Target Country.');
        if (countrySelect) countrySelect.focus();
        return;
      }

      if (!jd) {
        showError('Please paste the Job Description.');
        if (jdTextarea) jdTextarea.focus();
        return;
      }

      if (jd.length < 30) {
        showError('Job Description is too short. Please paste the full job description for optimal ATS targeting.');
        if (jdTextarea) jdTextarea.focus();
        return;
      }

      const payload = {
        company: company,
        country: country,
        jd: jd,
        ai_provider: ai_provider
      };

      setLoadingState(true);

      try {
        const response = await fetch('/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        const data = await response.json().catch(() => null);

        setLoadingState(false);

        if (response.ok && data && data.success) {
          showSuccess(data);

          saveHistoryItem({
            id: 'rt_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5),
            company: company,
            country: country,
            ai_provider: ai_provider,
            filename: data.filename || `${company}_Resume.pdf`,
            pdf_path: data.pdf_path || '',
            timestamp: new Date().toISOString()
          });

        } else {
          const errDetail = (data && data.message) ? data.message : `Server returned status ${response.status}: ${response.statusText}`;
          showError(errDetail);
        }
      } catch (networkError) {
        console.error('Fetch error:', networkError);
        setLoadingState(false);
        showError('Network connection failed or server unreachable. Please verify your backend server is running at /generate.');
      }
    });
  }

})();
