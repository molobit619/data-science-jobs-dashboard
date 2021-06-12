// set the dimensions and margins of the graph
var svgWidth = 750;
var svgHeight = 670;

var margin = {
top:40, right: 30, bottom: 55, left: 100}

var width = svgWidth - margin.left - margin.right;
var height = svgHeight - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select('#hld3')
  .append('svg')
  .attr('width', svgWidth)
  .attr('height', svgHeight);

// append an SVG group that will hold the chart, and shift chart by left and top margins.
var chartGroup = svg.append('g')
  .attr('transform', `translate(${margin.left}, ${margin.top})`);

  // import data
d3.csv('static/data/avgsalary.csv').then(data => {
    // cast avg_salary as numbers
    data.forEach(datum => {
      datum.avg_salary = +datum.avg_salary;
    });

    // sort data in descending avg salary
    data.sort((a, b) => a.avg_salary - b.avg_salary);

    // create scale functions
    var x = d3.scaleLinear()
      .domain([0, d3.max(data, d=> d.avg_salary)+10])
      .range([0, width]);

    var y = d3.scaleBand()
      .domain(data.map(d => d.job_state))
      .range([height, 0])
      .padding(1);

    // create axis functions
    var bottomAxis = d3.axisBottom(x);
    var leftAxis = d3.axisLeft(y);

    // append axes to the chart
    chartGroup.append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(bottomAxis);
    
    chartGroup.append('g')
      .call(leftAxis);

    // create lines
    chartGroup.selectAll('myline')
      .data(data)
      .enter()
      .append("line")
      .attr("x1", x(0))
      .attr("x2", x(0))
      .attr("y1", d => y(d.job_state))
      .attr("y2", d => y(d.job_state))
      .attr("stroke", "#1E2FE2"
      );

    // Circles -> start at X=0
    chartGroup.selectAll("mycircle")
      .data(data)
      .enter()
      .append("circle")
        .attr("cx", x(0) )
        .attr("cy", d => y(d.job_state))
        .attr("r", "6")
        .style("fill", "#1ECFE2")
        .attr("stroke", "black");

    // Change the X coordinates of line and circle. Transition for 3 seconds.
    chartGroup.selectAll("circle")
      .transition()
      .duration(4000)
      .attr("cx", d => x(d.avg_salary));

    chartGroup.selectAll("line")
      .transition()
      .duration(4000)
      .attr("x1", d => x(d.avg_salary));

    // create axes labels
    chartGroup.append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 0 - margin.left + 40)
    .attr("x", -90 - (height/2.7))
    .attr("dy", "1em")
    .attr("class", "ylabel")
    .attr("font-size", "18px")
    .text("State");

    chartGroup.append("text")
    .attr("class", "xlabel")
    .attr("text-anchor", "end")
    .attr("x", width-190)
    .attr("y", height + 40)
    .attr("font-size", "18px")
    .text("Salary (USD, in thousand)");
      
}).catch(error => console.log(error));