/**
 * Main JavaScript for Artur Riazanov's homepage
 * Handles paper filtering, abstract toggling, and dynamic paper loading
 */

// Global paper registry
// Format: [paperId, topics[]]
var paper_id_list = [];

// Cache for loaded papers
let papersCache = null;

// SVG icon highlighting is now handled via CSS classes

/**
 * Toggles visibility of a paper's abstract
 * Loads abstract on demand if not already loaded
 * @param {string} id - The paper ID (title-based, max 15 chars)
 */
async function toggleVisibility(id) {
    const abstractElement = document.getElementById(`abstract${id}`);
    if (!abstractElement) {
        return;
    }
    
    // Check if currently hidden by checking computed style
    const computedStyle = window.getComputedStyle(abstractElement);
    const isHidden = computedStyle.display === 'none' || abstractElement.classList.contains('hidden');
    
    // Load abstract if hidden and not yet loaded
    if (isHidden && !abstractElement.dataset.loaded) {
        const abstractHtml = await loadAbstract(id);
        if (abstractHtml) {
            abstractElement.innerHTML = abstractHtml;
            abstractElement.dataset.loaded = 'true';
            
            // Re-render Math if KaTeX is available
            if (typeof renderMathInElement !== 'undefined') {
                renderMathInElement(abstractElement);
            }
        }
    }
    
    // Toggle visibility
    if (isHidden) {
        abstractElement.classList.remove('hidden');
        abstractElement.style.display = 'block';
    } else {
        abstractElement.classList.add('hidden');
        abstractElement.style.display = 'none';
    }
}

/**
 * Filters papers by topic
 * @param {string} topic - The topic to filter by ('all' shows all papers)
 */
function filterPapers(topic) {
    const papersContainer = document.getElementById('papers-container');
    if (!papersContainer) {
        return;
    }

    // Show papers container
    papersContainer.classList.remove('papers-container-hidden');
    papersContainer.style.display = 'block';

    // Filter papers
    paper_id_list.forEach(([paperId, topics]) => {
        const paperElement = document.getElementById(paperId);
        if (!paperElement) {
            return;
        }

        const isTopical = topic === 'all' || topics.includes(topic);
        if (isTopical) {
            paperElement.style.display = 'block';
            paperElement.classList.remove('hidden');
        } else {
            paperElement.style.display = 'none';
            paperElement.classList.add('hidden');
        }
    });

    // Remove active class from all topic icons
    document.querySelectorAll('.paper-topic-icon').forEach(icon => {
        icon.classList.remove('active');
    });

    // Add active class to selected topic icon
    const topicIcon = document.getElementById(`${topic}-icon`);
    if (topicIcon) {
        topicIcon.classList.add('active');
    }
    
    // Show topic name
    showTopicName(topic);
}

/**
 * Format topic name for display (convert dashes to spaces and capitalize)
 * @param {string} topic - The topic ID (e.g., 'proof-complexity')
 * @returns {string} Formatted topic name (e.g., 'Proof Complexity')
 */
function formatTopicName(topic) {
    if (topic === 'all') {
        return 'All Papers';
    }
    return topic
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

/**
 * Show topic name in the display area
 * @param {string} topic - The topic ID
 */
function showTopicName(topic) {
    const topicNameDisplay = document.getElementById('topic-name-display');
    if (topicNameDisplay) {
        topicNameDisplay.textContent = formatTopicName(topic);
        topicNameDisplay.classList.add('visible');
    }
}

/**
 * Hide topic name display (used on mouseleave)
 */
function hideTopicName() {
    const topicNameDisplay = document.getElementById('topic-name-display');
    const activeIcon = document.querySelector('.paper-topic-icon.active');
    
    // Only hide if no topic is currently active
    if (topicNameDisplay && !activeIcon) {
        topicNameDisplay.classList.remove('visible');
        topicNameDisplay.textContent = '';
    } else if (topicNameDisplay && activeIcon) {
        // Keep showing the active topic name
        const activeTopicId = activeIcon.id.replace('-icon', '');
        showTopicName(activeTopicId);
    }
}

/**
 * Check if we're running from file:// protocol
 * @returns {boolean} True if using file:// protocol
 */
function isFileProtocol() {
    return window.location.protocol === 'file:';
}

/**
 * Load papers from data.json
 * @returns {Promise<Array>} Array of paper objects
 */
async function loadPapers() {
    if (papersCache) {
        return papersCache;
    }
    
    // Check if we're using file:// protocol (local file system)
    if (isFileProtocol()) {
        throw new Error('FILE_PROTOCOL_ERROR');
    }
    
    try {
        const response = await fetch('data.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const papers = await response.json();
        
        // Sort by date (newest first)
        papers.sort((a, b) => {
            const dateA = new Date(a.date).getTime();
            const dateB = new Date(b.date).getTime();
            return dateB - dateA;
        });
        
        papersCache = papers;
        return papers;
    } catch (error) {
        console.error('Error loading papers:', error);
        throw error;
    }
}

/**
 * Load abstract from abstracts directory
 * @param {string} paperId - The paper ID
 * @returns {Promise<string>} Abstract HTML content
 */
async function loadAbstract(paperId) {
    try {
        const response = await fetch(`abstracts/${paperId}.html`);
        if (!response.ok) {
            return '';
        }
        return await response.text();
    } catch (error) {
        console.error(`Error loading abstract for ${paperId}:`, error);
        return '';
    }
}

/**
 * Render a single paper to HTML
 * @param {Object} paper - Paper object
 * @param {string} abstractHtml - Abstract HTML content
 * @returns {string} HTML string for the paper
 */
function renderPaper(paper, abstractHtml = '') {
    const paperId = paper.paper_id;
    const topicIcons = paper.topics.map(topic => 
        `<div><img src="${topic}.svg" class="topic-icon"></div>`
    ).join('\n        ');
    
    const authors = paper.author.map(author => 
        `<a href="${author.url}" class="inside-post">${escapeHtml(author.name)}</a>`
    ).join('\n        ');
    
    const links = paper.links.map(link => {
        const target = link.url.includes('http') ? ' target="_blank"' : '';
        return `<a href="${link.url}" class="inside-post"${target}>${escapeHtml(link.name)}</a>`;
    }).join('\n        ');
    
    return `
        <div class="post-row" id="paper-${paperId}">
            <div class="post-heading">
                ${topicIcons}
                <div>
                    <h3 class="paper-header" onclick="toggleVisibility('${paperId}')">${escapeHtml(paper.title)}</h3>
                </div>
            </div>
            <div class="paper-authors">
                <div class="paper-authors-label">Authors: </div>
                ${authors}
            </div>
            <div class="paper-links">
                ${links}
            </div>
            <div id="abstract${paperId}" class="abstract">
                ${abstractHtml}
            </div>
        </div>
    `;
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Render all papers to the papers container
 * @param {Array} papers - Array of paper objects
 */
async function renderPapers(papers) {
    const container = document.getElementById('papers-container');
    if (!container) {
        return;
    }
    
    // Clear existing content
    container.innerHTML = '';
    
    // Reset paper_id_list (clear array, don't reassign to maintain reference)
    paper_id_list.length = 0;
    
    // Render each paper
    for (const paper of papers) {
        const paperId = paper.paper_id;
        
        // Register paper for filtering
        paper_id_list.push([`paper-${paperId}`, paper.topics]);
        
        // Render paper (abstracts loaded on demand)
        const paperHtml = renderPaper(paper, '');
        container.insertAdjacentHTML('beforeend', paperHtml);
    }
}

/**
 * Load and render papers dynamically
 */
async function loadAndRenderPapers() {
    const container = document.getElementById('papers-container');
    const loadingElement = document.getElementById('papers-loading');
    
    try {
        const papers = await loadPapers();
        if (papers.length > 0) {
            if (loadingElement) {
                loadingElement.remove();
            }
            await renderPapers(papers);
        } else if (loadingElement) {
            loadingElement.textContent = 'No papers found.';
        }
    } catch (error) {
        console.error('Error loading papers:', error);
        if (loadingElement) {
            if (error.message === 'FILE_PROTOCOL_ERROR') {
                // Show helpful message for file:// protocol
                loadingElement.innerHTML = `
                    <div class="error-message">
                        <p><strong>Local Development Notice</strong></p>
                        <p>This site needs to be served via HTTP. Please run a local server:</p>
                        <pre>
cd ${window.location.pathname.split('/').slice(0, -1).join('/') || '.'}
python3 -m http.server 8000
                        </pre>
                        <p>Then open <a href="http://localhost:8000">http://localhost:8000</a></p>
                        <p><em>On GitHub Pages, this will work automatically.</em></p>
                    </div>
                `;
            } else {
                loadingElement.textContent = 'Error loading papers.';
            }
        }
    }
}

/**
 * Initialize page functionality
 */
async function initializePage() {
    // Load and render papers
    await loadAndRenderPapers();
    
    // Placeholder for future initialization code
    // Previously had analytics code commented out:
    // fetch("https://tunyash.pythonanywhere.com/clicked")
    //     .then((response) => response.json())
    //     .then((json) => console.log(json));
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePage);
} else {
    initializePage();
}

// Export functions to global scope for compatibility with inline scripts and onclick handlers
window.paper_id_list = paper_id_list;
window.toggleVisibility = toggleVisibility;
window.filterPapers = filterPapers;
window.getData = initializePage;
window.showTopicName = showTopicName;
window.hideTopicName = hideTopicName;

