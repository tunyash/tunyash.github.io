/**
 * Main JavaScript for Artur Riazanov's homepage
 * Handles paper filtering and abstract toggling
 */

// Global paper registry - populated by inline scripts in generated HTML
// Format: [paperId, topics[]]
// Using var for compatibility with inline scripts that reference paper_id_list
var paper_id_list = [];

// State for SVG icon highlighting
let svgRevertState = [];

/**
 * Toggles visibility of a paper's abstract
 * @param {string} id - The paper ID (title-based, max 15 chars)
 */
function toggleVisibility(id) {
    const abstractElement = document.getElementById(`abstract${id}`);
    if (abstractElement) {
        const isHidden = abstractElement.style.display === 'none';
        abstractElement.style.display = isHidden ? 'block' : 'none';
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
    papersContainer.style.display = 'block';

    // Filter papers
    paper_id_list.forEach(([paperId, topics]) => {
        const paperElement = document.getElementById(paperId);
        if (!paperElement) {
            return;
        }

        const isTopical = topic === 'all' || topics.includes(topic);
        paperElement.style.display = isTopical ? 'block' : 'none';
    });

    // Restore previous SVG states
    svgRevertState.forEach(([elementId, originalStroke, originalFill]) => {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.stroke = originalStroke;
            element.style.fill = originalFill;
        }
    });

    // Clear revert state
    svgRevertState = [];

    // Highlight selected topic SVG icon
    const topicSvg = document.querySelector(`#${topic}-svg`);
    if (topicSvg) {
        const svgElements = topicSvg.querySelectorAll('path, rect, circle, ellipse');
        svgElements.forEach((element) => {
            const currentStroke = element.style.stroke || '';
            const currentFill = element.style.fill || '';
            
            // Save original state
            svgRevertState.push([element.id, currentStroke, currentFill]);
            
            // Apply highlight
            element.style.stroke = 'blue';
            if (element.style.fill !== 'none') {
                element.style.fill = 'blue';
            }
        });
    }
}

/**
 * Initialize page functionality
 * Currently placeholder for future analytics or initialization code
 */
function initializePage() {
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

