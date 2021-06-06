/* load csv data in db before running any other endpoints*/
d3.json("/api/data-science/load-data").then(data => {
    console.log(`total entries loaded: ${data['total_entries']}`);

    d3.json("/api/data-science/job-openings/totals_by_position").then(data => {
        console.log(data);
        d3.select('#jobs_by_position')
            .selectAll('ul')
            .data(data)
            .enter()
            .append('li')
            .text(entry => entry[0])
    });

    d3.json("/api/data-science/highest-demand").then(data => {
        console.log(data);
    });

    d3.json("/api/data-science/average-salary").then(data => {
        console.log(data);
    });
});
