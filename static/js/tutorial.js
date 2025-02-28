// Tutorial steps configuration
const tutorialSteps = {
    welcome: [
        {
            element: '#game-overview',
            title: 'Welcome to Business Game',
            intro: 'This tutorial will guide you through the basics of running your company.',
            position: 'bottom'
        }
    ],
    basicMetrics: [
        {
            element: '#cash-metric',
            title: 'Cash',
            intro: 'Your available cash for operations and investments.',
            position: 'bottom'
        },
        {
            element: '#market-share-metric',
            title: 'Market Share',
            intro: 'Your company\'s share of the total market.',
            position: 'bottom'
        },
        {
            element: '#stock-price-metric',
            title: 'Stock Price',
            intro: 'The current value of your company\'s stock, reflecting overall performance.',
            position: 'bottom'
        }
    ],
    decisions: [
        {
            element: '#production-section',
            title: 'Production Decisions',
            intro: 'Set your production volume and manage capacity.',
            position: 'right'
        },
        {
            element: '#pricing-section',
            title: 'Pricing Strategy',
            intro: 'Set your product price based on market conditions and costs.',
            position: 'left'
        },
        {
            element: '#marketing-section',
            title: 'Marketing',
            intro: 'Invest in marketing to increase brand awareness and sales.',
            position: 'right'
        }
    ],
    advancedFeatures: [
        {
            element: '#hr-section',
            title: 'Human Resources',
            intro: 'Manage your workforce through hiring, training, and development.',
            position: 'left'
        },
        {
            element: '#international-section',
            title: 'International Operations',
            intro: 'Expand your business globally through various entry modes.',
            position: 'right'
        },
        {
            element: '#supply-chain-section',
            title: 'Supply Chain',
            intro: 'Optimize your supply chain for efficiency and resilience.',
            position: 'left'
        }
    ]
};

// Feature-specific tutorials
const featureTutorials = {
    hr: [
        {
            element: '#hiring-form',
            title: 'Hiring',
            intro: 'Hire new employees by specifying department, count, and requirements.'
        },
        {
            element: '#training-form',
            title: 'Training Programs',
            intro: 'Invest in employee development to improve skills and satisfaction.'
        },
        {
            element: '#salary-adjustments',
            title: 'Salary Management',
            intro: 'Adjust salaries to maintain employee satisfaction and retention.'
        }
    ],
    international: [
        {
            element: '#region-selection',
            title: 'Region Selection',
            intro: 'Choose regions for international expansion.'
        },
        {
            element: '#entry-mode',
            title: 'Entry Mode',
            intro: 'Select how you want to enter the market: export, partnership, or subsidiary.'
        },
        {
            element: '#currency-management',
            title: 'Currency Management',
            intro: 'Manage currency exposure and hedging strategies.'
        }
    ],
    supplyChain: [
        {
            element: '#supplier-management',
            title: 'Supplier Management',
            intro: 'Manage relationships with suppliers and optimize lead times.'
        },
        {
            element: '#inventory-management',
            title: 'Inventory Management',
            intro: 'Balance inventory levels to minimize costs while meeting demand.'
        },
        {
            element: '#disruption-management',
            title: 'Disruption Management',
            intro: 'Prepare for and respond to supply chain disruptions.'
        }
    ]
};

// Context-sensitive help
const contextHelp = {
    pricing: {
        title: 'Pricing Strategy',
        content: `
            <h5>Factors to Consider:</h5>
            <ul>
                <li>Market demand elasticity</li>
                <li>Competitor prices</li>
                <li>Production costs</li>
                <li>Target market segment</li>
            </ul>
            <h5>Tips:</h5>
            <ul>
                <li>Higher prices may reduce demand but increase margins</li>
                <li>Consider promotional pricing for market penetration</li>
                <li>Monitor competitor reactions to price changes</li>
            </ul>
        `
    },
    marketing: {
        title: 'Marketing Strategy',
        content: `
            <h5>Key Components:</h5>
            <ul>
                <li>Budget allocation</li>
                <li>Channel mix</li>
                <li>Campaign focus</li>
                <li>Target segments</li>
            </ul>
            <h5>Tips:</h5>
            <ul>
                <li>Balance traditional and digital channels</li>
                <li>Align marketing with pricing strategy</li>
                <li>Track marketing effectiveness metrics</li>
            </ul>
        `
    }
    // Add more context help topics...
};

// Start the main tutorial
function startTutorial() {
    const intro = introJs();
    intro.setOptions({
        steps: [
            ...tutorialSteps.welcome,
            ...tutorialSteps.basicMetrics,
            ...tutorialSteps.decisions
        ],
        showProgress: true,
        showBullets: false,
        showStepNumbers: true,
        exitOnOverlayClick: false,
        exitOnEsc: true,
        nextLabel: 'Next →',
        prevLabel: '← Back',
        doneLabel: 'Finish'
    });
    
    intro.start();
}

// Start a feature-specific tutorial
function startFeatureTutorial(feature) {
    if (featureTutorials[feature]) {
        const intro = introJs();
        intro.setOptions({
            steps: featureTutorials[feature],
            showProgress: true,
            showBullets: false,
            showStepNumbers: true
        });
        intro.start();
    }
}

// Show context-sensitive help
function showContextHelp(topic) {
    if (contextHelp[topic]) {
        const helpModal = new bootstrap.Modal(document.getElementById('helpModal'));
        document.getElementById('helpModalTitle').textContent = contextHelp[topic].title;
        document.getElementById('helpModalContent').innerHTML = contextHelp[topic].content;
        helpModal.show();
    }
}

// Initialize help triggers
document.addEventListener('DOMContentLoaded', function() {
    // Add help triggers to elements
    document.querySelectorAll('[data-help-topic]').forEach(element => {
        element.addEventListener('click', (e) => {
            e.preventDefault();
            showContextHelp(element.dataset.helpTopic);
        });
    });
    
    // Add feature tutorial triggers
    document.querySelectorAll('[data-feature-tutorial]').forEach(element => {
        element.addEventListener('click', (e) => {
            e.preventDefault();
            startFeatureTutorial(element.dataset.featureTutorial);
        });
    });
}); 