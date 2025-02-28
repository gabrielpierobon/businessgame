// Market Segment Treemap
function createMarketSegmentTreemap(data, containerId) {
    const width = 600;
    const height = 400;
    
    const svg = d3.select(containerId)
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    const root = d3.hierarchy(data)
        .sum(d => d.size);
    
    d3.treemap()
        .size([width, height])
        .padding(2)
        (root);
    
    const cell = svg.selectAll("g")
        .data(root.leaves())
        .enter().append("g")
        .attr("transform", d => `translate(${d.x0},${d.y0})`);
    
    cell.append("rect")
        .attr("width", d => d.x1 - d.x0)
        .attr("height", d => d.y1 - d.y0)
        .attr("fill", d => d.data.color);
    
    cell.append("text")
        .attr("x", 5)
        .attr("y", 20)
        .text(d => d.data.name);
}

// International Operations Map
function createWorldMap(data, containerId) {
    // World map visualization using D3.js
    // Implementation will use D3's geo projection and path generators
    // to create an interactive world map showing company operations
}

// HR Metrics Dashboard
function createHRDashboard(data) {
    // Employee satisfaction chart
    new Chart(document.getElementById('satisfactionChart'), {
        type: 'line',
        data: {
            labels: data.quarters,
            datasets: [{
                label: 'Employee Satisfaction',
                data: data.satisfaction,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        }
    });
    
    // Productivity chart
    new Chart(document.getElementById('productivityChart'), {
        type: 'line',
        data: {
            labels: data.quarters,
            datasets: [{
                label: 'Productivity',
                data: data.productivity,
                borderColor: 'rgb(153, 102, 255)',
                tension: 0.1
            }]
        }
    });
    
    // Department breakdown
    new Chart(document.getElementById('departmentChart'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(data.departments),
            datasets: [{
                data: Object.values(data.departments).map(d => d.length),
                backgroundColor: [
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 206, 86)',
                    'rgb(75, 192, 192)'
                ]
            }]
        }
    });
}

// Supply Chain Network
function createSupplyChainNetwork(data, containerId) {
    const width = 800;
    const height = 600;
    
    const svg = d3.select(containerId)
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id(d => d.id))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));
    
    const link = svg.append("g")
        .selectAll("line")
        .data(data.links)
        .enter().append("line")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6);
    
    const node = svg.append("g")
        .selectAll("circle")
        .data(data.nodes)
        .enter().append("circle")
        .attr("r", 5)
        .attr("fill", d => d.color);
    
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        
        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
    });
}

// Competitor Analysis Radar Chart
function createCompetitorRadar(data) {
    new Chart(document.getElementById('competitorRadar'), {
        type: 'radar',
        data: {
            labels: ['Market Share', 'Price Position', 'Product Quality', 'Brand Strength', 'Innovation', 'Supply Chain'],
            datasets: [
                {
                    label: 'Your Company',
                    data: data.player,
                    fill: true,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgb(54, 162, 235)',
                    pointBackgroundColor: 'rgb(54, 162, 235)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(54, 162, 235)'
                },
                {
                    label: 'Industry Average',
                    data: data.industry,
                    fill: true,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgb(255, 99, 132)',
                    pointBackgroundColor: 'rgb(255, 99, 132)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(255, 99, 132)'
                }
            ]
        },
        options: {
            elements: {
                line: {
                    borderWidth: 3
                }
            }
        }
    });
}

// Decision Impact Preview
function updateDecisionPreview(decisions) {
    // Calculate and display estimated impacts of current decisions
    const impacts = calculateDecisionImpacts(decisions);
    
    // Update preview displays
    Object.entries(impacts).forEach(([metric, value]) => {
        const element = document.getElementById(`${metric}Preview`);
        if (element) {
            const change = value.change > 0 ? `+${value.change}` : value.change;
            element.innerHTML = `
                <div class="preview-value ${value.change > 0 ? 'positive' : 'negative'}">
                    ${change}%
                </div>
                <div class="preview-description">${value.description}</div>
            `;
        }
    });
}

function calculateDecisionImpacts(decisions) {
    // Implement impact calculations based on current decisions
    // This is a simplified example
    return {
        revenue: {
            change: (decisions.price - 100) * -0.5 + (decisions.marketing_budget * 0.2),
            description: "Based on price elasticity and marketing effectiveness"
        },
        marketShare: {
            change: (100 - decisions.price) * 0.1 + (decisions.marketing_budget * 0.15),
            description: "Influenced by competitive pricing and marketing"
        },
        // Add more metrics...
    };
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    tippy('[data-tippy-content]');
}); 