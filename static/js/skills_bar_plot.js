function showTable(response, elementId) {
    const {columns, data, index} = response;
    const tableData = index.map(i => {
        let dataSet = {};

        columns.forEach((col, j) => {
            dataSet[col] = data[i][j];
        });

        return dataSet;
    });

    const table = d3.select(`#${elementId}`).append('table')
        .attr('class', 'table')
        .attr('width', '80%')
    ;

    const thead = table.append('thead');
    const tbody = table.append('tbody');

    thead.append('tr')
        .selectAll('th')
        .data(columns)
        .enter()
        .append('th')
        .attr('width', '15%')
        .text(entry => entry.replace('_', ' '));

    tbody.selectAll('tr')
        .data(tableData)
        .enter()
        .append('tr')
        .html(row => {
            return Object.values(row).map(col => { return `<td>${col}</td>`; }).join('');
        });
}

function createBarPlot(response) {
  // Define SVG area dimensions
  const svgWidth = 500;
  const svgHeight = 300;

  // Define the chart's margins as an object
  const chartMargin = {
    top: 30,
    right: 30,
    bottom: 30,
    left: 30
  };

  // Define dimensions of the chart area
  const chartWidth = svgWidth - chartMargin.left - chartMargin.right;
  const chartHeight = svgHeight - chartMargin.top - chartMargin.bottom;

  // Select body, append SVG area to it, and set the dimensions
  const svg = d3.select("#skills_chart")
    .append("svg")
    .attr("height", svgHeight)
    .attr("width", svgWidth);

  // Append a group to the SVG area and shift ('translate') it to the right and to the bottom
  const chartGroup = svg.append("g")
    .attr("transform", `translate(${chartMargin.left}, ${chartMargin.top})`);

  const {columns, data} = response;
  const chartData = columns.map((entry, i) => {
        return ({
            skill: entry,
            total: data[0][i]
        });
    });

  var xBandScale = d3.scaleBand()
    .domain(chartData.map(d => d.skill))
    .range([0, chartWidth])
    .padding(0.1);

  var yLinearScale = d3.scaleLinear()
    .domain([0, d3.max(chartData, d => d.total)])
    .range([chartHeight, 0]);

  var bottomAxis = d3.axisBottom(xBandScale);
  var leftAxis = d3.axisLeft(yLinearScale).ticks(10);

  chartGroup.append("g")
    .call(leftAxis);

  chartGroup.append("g")
    .attr("transform", `translate(0, ${chartHeight})`)
    .call(bottomAxis);

  chartGroup.selectAll(".bar")
    .data(chartData)
    .enter()
    .append("rect")
    .attr("class", "bar")
    .attr("x", d => xBandScale(d.skill))
    .attr("y", d => yLinearScale(d.total))
    .attr("width", xBandScale.bandwidth())
    .attr("height", d => chartHeight - yLinearScale(d.total))
    .on('click', entry => {
      // reset previously selected bars
      d3.selectAll('.active').attr('class', 'bar', true);
        // set new bar to active
        const activeBar = d3.select(d3.event.target).attr('class', 'bar active', true);

        // clear table contents
        d3.select(`#positions-table`).html('');

        d3.json(`/api/data-science/skills/top_positions_by_tech/${entry.skill}`).then((data) => {
          showTable(data, 'positions-table');

          d3.select('#summary').style('display', 'block');
          d3.select('#summary').select('h3').text(entry.skill);
          d3.select('#summary').select('span').text(entry.total);
      });

    });
    ;
}
