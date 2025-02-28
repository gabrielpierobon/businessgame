// Help content configuration
const helpContent = {
    basics: {
        title: 'Game Basics',
        sections: [
            {
                title: 'Getting Started',
                content: `
                    <p>Business Game is a turn-based simulation where you manage a manufacturing company. Each turn represents one quarter of business operations.</p>
                    <h6>Key Metrics:</h6>
                    <ul>
                        <li>Cash - Available funds for operations and investments</li>
                        <li>Market Share - Your portion of the total market</li>
                        <li>Stock Price - Overall company value indicator</li>
                    </ul>
                `
            },
            {
                title: 'Core Decisions',
                content: `
                    <h6>Each quarter you make decisions about:</h6>
                    <ul>
                        <li>Production volume</li>
                        <li>Product pricing</li>
                        <li>Marketing investments</li>
                        <li>Research & Development</li>
                    </ul>
                `
            }
        ]
    },
    production: {
        title: 'Production Management',
        sections: [
            {
                title: 'Capacity Planning',
                content: `
                    <p>Manage your production capacity to meet market demand efficiently.</p>
                    <h6>Key Considerations:</h6>
                    <ul>
                        <li>Current capacity utilization</li>
                        <li>Expansion costs and lead time</li>
                        <li>Market growth projections</li>
                    </ul>
                `
            },
            {
                title: 'Inventory Management',
                content: `
                    <p>Balance inventory levels to minimize costs while meeting demand.</p>
                    <h6>Costs to Consider:</h6>
                    <ul>
                        <li>Storage costs</li>
                        <li>Stockout risks</li>
                        <li>Production efficiency</li>
                    </ul>
                `
            }
        ]
    },
    hr: {
        title: 'Human Resources',
        sections: [
            {
                title: 'Workforce Management',
                content: `
                    <h6>Key HR Functions:</h6>
                    <ul>
                        <li>Hiring new employees</li>
                        <li>Training programs</li>
                        <li>Salary management</li>
                        <li>Employee satisfaction</li>
                    </ul>
                    <p>Balance costs with productivity and satisfaction.</p>
                `
            },
            {
                title: 'Department Management',
                content: `
                    <h6>Departments:</h6>
                    <ul>
                        <li>Production - Manufacturing efficiency</li>
                        <li>R&D - Product innovation</li>
                        <li>Marketing - Market effectiveness</li>
                        <li>Supply Chain - Logistics optimization</li>
                    </ul>
                `
            }
        ]
    },
    international: {
        title: 'International Operations',
        sections: [
            {
                title: 'Market Entry',
                content: `
                    <h6>Entry Modes:</h6>
                    <ul>
                        <li>Export - Low risk, limited control</li>
                        <li>Partnership - Shared risk and control</li>
                        <li>Subsidiary - High control, high risk</li>
                    </ul>
                `
            },
            {
                title: 'Regional Management',
                content: `
                    <h6>Key Considerations:</h6>
                    <ul>
                        <li>Market size and growth</li>
                        <li>Cultural distance</li>
                        <li>Regulatory environment</li>
                        <li>Currency risk</li>
                    </ul>
                `
            }
        ]
    },
    supplyChain: {
        title: 'Supply Chain Management',
        sections: [
            {
                title: 'Supplier Relations',
                content: `
                    <h6>Key Metrics:</h6>
                    <ul>
                        <li>Supplier quality</li>
                        <li>Lead times</li>
                        <li>Relationship strength</li>
                        <li>Cost efficiency</li>
                    </ul>
                `
            },
            {
                title: 'Risk Management',
                content: `
                    <h6>Types of Risks:</h6>
                    <ul>
                        <li>Supplier bankruptcy</li>
                        <li>Natural disasters</li>
                        <li>Logistics disruptions</li>
                        <li>Quality issues</li>
                    </ul>
                `
            }
        ]
    }
};

// Load help content into accordion
function loadHelpContent() {
    const accordion = document.getElementById('helpAccordion');
    if (!accordion) return;
    
    accordion.innerHTML = '';
    
    Object.entries(helpContent).forEach(([key, section], index) => {
        const accordionItem = document.createElement('div');
        accordionItem.className = 'accordion-item';
        
        accordionItem.innerHTML = `
            <h2 class="accordion-header" id="heading${key}">
                <button class="accordion-button ${index > 0 ? 'collapsed' : ''}" type="button" 
                        data-bs-toggle="collapse" data-bs-target="#collapse${key}">
                    ${section.title}
                </button>
            </h2>
            <div id="collapse${key}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}"
                 data-bs-parent="#helpAccordion">
                <div class="accordion-body">
                    ${section.sections.map(subsection => `
                        <div class="help-section mb-4">
                            <h5>${subsection.title}</h5>
                            ${subsection.content}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        accordion.appendChild(accordionItem);
    });
}

// Search help content
function searchHelp(query) {
    query = query.toLowerCase();
    const results = [];
    
    Object.entries(helpContent).forEach(([key, section]) => {
        section.sections.forEach(subsection => {
            if (subsection.title.toLowerCase().includes(query) ||
                subsection.content.toLowerCase().includes(query)) {
                results.push({
                    section: section.title,
                    title: subsection.title,
                    content: subsection.content
                });
            }
        });
    });
    
    return results;
}

// Show quick help tooltip
function showQuickHelp(element, topic) {
    tippy(element, {
        content: helpContent[topic]?.sections[0]?.content || 'Help content not found',
        allowHTML: true,
        interactive: true,
        maxWidth: 300,
        placement: 'right'
    });
}

// Initialize help system
document.addEventListener('DOMContentLoaded', function() {
    // Load help content when modal opens
    const helpModal = document.getElementById('helpModal');
    if (helpModal) {
        helpModal.addEventListener('show.bs.modal', loadHelpContent);
    }
    
    // Initialize quick help tooltips
    document.querySelectorAll('[data-quick-help]').forEach(element => {
        showQuickHelp(element, element.dataset.quickHelp);
    });
    
    // Initialize help search
    const searchInput = document.getElementById('helpSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const results = searchHelp(e.target.value);
            // Update search results display
            const resultsContainer = document.getElementById('searchResults');
            if (resultsContainer) {
                resultsContainer.innerHTML = results.map(result => `
                    <div class="search-result">
                        <h6>${result.section} - ${result.title}</h6>
                        ${result.content}
                    </div>
                `).join('');
            }
        });
    }
}); 