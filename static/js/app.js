/* load csv data in db before running any other endpoints*/
d3.json("/api/data-science/load-data").then(data => {
    console.log(`total entries loaded: ${data['total_entries']}`);

    d3.json("/api/data-science/job-openings/totals_by_position").then(data => {
        console.log(data);
        d3.select('#jobs_by_position')
            .append('table')
            .selectAll('tbody')
            .data(data)
            .enter()
            .append('tr')
            .html(entry => entry.map(col => {
                return `<td>${col}<td>`;
            }).join(''))
    });

    d3.select('#totals_by_industry')
        .attr("src", "/api/data-science/job-openings/totals_by_industry.png")
        .style("width", "25em")
        .style("height", "20em");

    d3.xml("/api/data-science/job-openings/average_salary.png").then(console.log);

    d3.json("/api/data-science/job-openings/totals_by_location").then(data => {
        console.log('totals_by_location: ', data);
    });

    d3.json("/api/data-science/highest-demand").then(data => {
        console.log(data);
    });

    d3.json("/api/data-science/average-salary").then(data => {
        console.log(data);
    });
});
